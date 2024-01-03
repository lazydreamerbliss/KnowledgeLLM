"""
Provide functionalities on feature extracting, retrieval, and reranking of documents.
"""
import os
import pickle

import numpy as np
import numpy.typing as npt
from numpy import ndarray
from sentence_transformers import CrossEncoder, SentenceTransformer
from faiss import IndexFlatL2, IndexIVFFlat  # Put faiss import AFTER sentence_transformers, strange SIGSEGV error otherwise
from tqdm import tqdm

from doc_functions.doc_provider import WechatHistoryProvider
from sqlite.wechat_history_table_sql import Record


class DocEmbedder:
    # "shibing624/text2vec-base-chinese" 预训练模型，用于将文本转换成向量 (https://huggingface.co/shibing624/text2vec-base-chinese)
    transformer_path: str = 'shibing624/text2vec-base-chinese'
    # "cross-encoder/ms-marco-MiniLM-L-12-v2" 预训练模型，用于比对检索到的文档，并对其按相似度重新排列，提高准确度
    cross_encoder_path: str = 'hfl/chinese-roberta-wwm-ext'

    def __init__(self, index_filename: str | None = None):
        # 初始化 SentenceTransformer 和 CrossEncoder 两个模型
        self.transformer: SentenceTransformer = SentenceTransformer(DocEmbedder.transformer_path)
        self.ranker: CrossEncoder = CrossEncoder(DocEmbedder.cross_encoder_path, max_length=512)
        self.index: IndexIVFFlat | None = None
        self.embeddings: ndarray | None = None
        self.doc_provider: WechatHistoryProvider | None = None

        if index_filename:
            if not os.path.exists(index_filename):
                return
            try:
                tqdm.write(f'Loading index from {index_filename}...')
                obj = pickle.load(open(index_filename, 'rb'))
                self.index = obj['index']
                self.embeddings = obj['embeddings']
                self.doc_provider = WechatHistoryProvider(obj['chat_name'])
            except:
                raise ValueError('Corrupted index file')

    def initialize(self, index_filename: str, chat_name: str, raw_doc_path: str | None, force_initialize: bool = False) -> None:
        """
        初始化相似度检索索引
        - Faiss 是 Meta 出品的相似度搜索框架，为海量稠密向量提供高效的相似度搜索和聚类

        选择索引方式是 faiss 的核心内容，faiss 三个最常用的索引是：IndexFlatL2/IndexFlatIP，IndexIVFFlat，IndexIVFPQ
        - IndexFlatL2/IndexFlatIP：直接暴力计算欧式距离来判断两个向量的相似度，适用于数据量较小的情况，效率最低（因为需要遍历所有向量），但精度最高
        - IndexIVFFlat：基于倒排表的分区索引，适用于数据量较大的情况，使用沃罗诺伊图划分高维空间中的点（通过 k-means 进行聚类训练）
        - IndexIVFPQ：是一种减少内存占用的索引方式，前两种会全量存储所有向量到内存中，而 IndexIVFPQ 会将向量分成多个倒排表子空间，并使用 PQ（乘积量化）压缩算法编码向量到指定字节数来减少内存
          - 由于存储的向量是经过 PQ 压缩的，所以在计算相似度时需要先解码，再计算相似度
        - https://zhuanlan.zhihu.com/p/90768014
        """
        if self.index and not force_initialize:
            return

        if not index_filename or not chat_name or not raw_doc_path:
            raise ValueError('Invalid arguments')

        self.doc_provider = WechatHistoryProvider(chat_name, raw_doc_path)

        # 向量化（embedding）是将文本转换成向量的过程，这里使用 SentenceTransformer 模型将文本转换成向量
        # - 向量化指把一个维数为所有词的数量的高维空间嵌入到一个维数低得多的连续向量空间中，每个单词或词组被映射为实数域上的向量
        # - https://zhuanlan.zhihu.com/p/26306795
        #
        # 调用模型 self.model.encode() 对每一个 doc 进行特征提取将其转换成向量，获得一个存储每个文档向量信息的列表
        # - 将该列表转化为 ndarray 二维矩阵，self.embeddings 的每一行表示一个文档的向量表示
        # -（tqdm 只是一个进度条库，用于显示特征提取的进度）
        tmp: list[ndarray] = [self.transformer.encode(f"{r.message}-{r.replied_message}") for r in
                              tqdm(self.doc_provider.get_all_records(), desc='Embedding data', ascii=' |')]  # type: ignore
        self.embeddings = np.asarray(tmp)

        # ndarray.shape 用于获取矩阵的维度，类型为元组。该元组的长度为数组的维度，每个元素表示数组在该维度上的长度
        # - 因为当前为二维矩阵，故 self.embeddings.shape 为一个长度为 2 的元组：shape[0] 表示文本数量，shape[1] 表示当前向量维度
        # - 例如：self.embeddings.shape 为 (1232, 76)，表示共有 1232 条文本，它们被转换成了 76 维的向量
        dimension: int = self.embeddings.shape[1]
        # 创建向量索引
        # - 这里获取第二纬度长度，并用其创建一个 IndexFlatIP 类型索引：self.index = IndexFlatIP(dimension)
        tqdm.write(f'Building index with dimension {dimension}...')
        quantizer: IndexFlatL2 = IndexFlatL2(dimension)
        self.index = IndexIVFFlat(quantizer, dimension, 50)

        # 将向量添加到索引
        # - 首先调用 self.index.train() 对索引进行聚类（即分区）训练
        # - 然后调用 self.index.add() 将向量添加到索引中
        #
        # 这里的类型报错是因为 faiss 库的类型定义和 numpy 库的类型定义不一致，但是不影响程序的运行
        # - faiss 的 add() 调用的是 IndexFlatCodes.add(n, x)，其两个参数 n 表示向量的数量，x 表示一个 n*d 的二维矩阵，d 为每一个向量的维度。而这里的 self.embeddings 是 numpy 的 ndarray 类型，其本身就是一个 n*d 的二维矩阵
        # - 可以将 add() 方法理解为接受一个矩阵作为参数，矩阵的每一行都是一个要添加的向量
        self.index.train(self.embeddings)  # type: ignore
        self.index.add(self.embeddings)  # type: ignore

        # 保存索引以便复用
        tqdm.write(f'Saving index to {index_filename}...')
        try:
            os.remove(index_filename)
        except:
            pass
        pickle.dump({'chat_name': chat_name, 'embeddings': self.embeddings,
                    'index': self.index}, open(index_filename, 'wb'))

        tqdm.write(f'Initialization completed')

    def __retrieve(self, text: str, top_k: int = 10) -> list[Record]:
        """
        从索引中检索与查询文本 text 最相似的 top_k 个文档
        :param text: 被查询的文本
        :param top_k: 检索到的最相似文档的最大数量
        """
        if not self.doc_provider or not self.index:
            raise ValueError('Not initialized')

        if not text or top_k <= 0:
            return list()

        # 调用 self.model.encode(x) 对查询文本进行特征提取，将其转换成向量
        tqdm.write(f'Querying top {top_k} candidates...')
        query_embedding: npt.ArrayLike = self.transformer.encode(text)

        # self.index.search() 进行精确内积搜索，获取 top_k 个相似向量，它返回两个矩阵作为结果：
        # - D：维度为 [查询向量样本数，top_k 相似向量数]，列表示第 n 个样本与 top_k 个相似向量的距离，距离从近到远排序
        # - I：维度为 [查询向量样本数，top_k 相似向量数]，列表示第 n 个样本在索引中 top_k 个相似向量的 id，相似度从高到低排序
        # - 例如：获取第 n 个样本的 top_k 个相似向量搜索结果，可以通过 D[n-1] 和 I[n-1] 获取
        # - https://www.cnblogs.com/luohenyueji/p/16990840.html
        D, I = self.index.search(np.asarray([query_embedding]), top_k)  # type: ignore

        # 通过检索到的文档矩阵，获取对应的原始文档
        # - 由于查询向量样本数为 1（只有一个 text），故 D 和 I 的都只有一行，所以这里只需要 I[0] 即可获得 top_k 个检索到的文档 id
        # - 通过文档 id 获取原始文档内容
        res: list[Record] = list()
        for i in I[0]:
            # Record ID starts from 1
            record: Record | None = self.doc_provider.get_record_by_id(int(i)+1)
            if record:
                res.append(record)
        return res

    def __rerank(self, text: str, candidates: list[Record]) -> list[Record]:
        """
        通过 CrossEncoder 模型对检索到的文档候选对象在语义相似度层面进行重新排序，以提高检索的准确性
        - CrossEncoder 会把两个句子进行拼接并输入到预训练模型中，使用 Transformer 进行更深层次的语义交互，然后接入一个分类层输出相似度的概率
        :param text: 被查询的文本
        :param candidates: top_k 个检索到的，与被查询文本最相似的文档
        """
        if not self.doc_provider or not self.index:
            raise ValueError('Not initialized')

        # CrossEncoder.predict() 接受一个二维矩阵作为参数进行相似度分析
        # - 矩阵的每一行都是一个要进行语义预测的样本，每一行的第一个元素是被查询文本（源文本），第二个元素是检索到的文档（目标文本）
        # - 返回一个一维矩阵，每一个元素都是对当前 text + doc 的预测分数（百分比），分数越高表示二者在语义上越相关
        # - https://aistudio.baidu.com/projectdetail/4951278
        tqdm.write(f'Reranking {len(candidates)} candidates...')
        merge: list[list[str]] = [
            [text, f"{_.message}-{_.replied_message}" if _.replied_message else _.message] for _ in candidates]
        scores: ndarray = self.ranker.predict(merge)  # type: ignore

        # 对分数进行排序，返回排序后的索引
        # - np.argsort() 返回的是给定数组值从小到大的索引值，故这里使用 [::-1] 将其反转，变成从大到小排序后的索引
        # - https://blog.csdn.net/maoersong/article/details/21875705
        sorted_ids: ndarray = np.argsort(scores)[::-1]

        # 最后根据排序后的索引，按新的顺序返回检索到的文档
        return [candidates[i] for i in sorted_ids]

    def query(self, query_text: str, top_k: int = 10, rerank: bool = False) -> list[Record]:
        tqdm.write(f'Q: {query_text}, get top {top_k} matches...')
        if rerank:
            candidates: list[Record] = self.__retrieve(query_text, top_k * 10)
            reranked: list[Record] = self.__rerank(query_text, candidates)
            return reranked[:top_k]

        return self.__retrieve(query_text, top_k)
