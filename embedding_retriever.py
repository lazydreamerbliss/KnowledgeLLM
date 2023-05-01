"""
Provide functionalities on feature extracting, retrieval, and reranking of documents.
"""
import numpy as np
import numpy.typing as npt
from typing import List, Optional, Mapping, Any
from glob import glob
from sentence_transformers import SentenceTransformer, CrossEncoder
from tqdm import tqdm
from faiss import IndexFlatIP
import pickle
from llama_model import AlpacaLora

class EmbeddingRetriever:
    def __init__(self, index_filename: str = None):
        if index_filename is not None:
            obj = pickle.load(open(index_filename, 'rb'))
            self.index = obj['index']
            self.documents = obj['documents']
            self.embeddings = obj['embeddings']
        else:
            self.index = None
            self.documents = None
        self.model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
    
    def extract_features_and_build_index(self, documents: List[str], output_filename: str, force_rebuild: bool = False) -> None:
        if self.index is not None and not force_rebuild:
            print('Index already exists, skipping...')
            return
        self.documents = documents
        self.embeddings = np.asarray([self.model.encode(x) for x in tqdm(documents, desc='Extracting features from documents...')])
        self.index = IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings)
        pickle.dump({
            'documents': self.documents,
            'embeddings': self.embeddings,
            'index': self.index,
        }, open(output_filename, 'wb'))

    def retrieve(self, query_embedding: npt.ArrayLike, top_k: int = 10) -> List[str]:
        inner_products, ids = self.index.search(np.asarray([query_embedding]), top_k)
        return [self.documents[i] for i in ids[0]]

    def rerank(self, query: str, candidates: List[str]) -> List[str]:
        scores = self.reranker.predict([(query, x) for x in candidates])
        ids = np.argsort(scores)[::-1]
        return [candidates[i] for i in ids]

    def query(self, query: str, top_k: int = 10) -> List[str]:
        query_embedding = self.model.encode(query)
        candidates = self.retrieve(query_embedding, top_k * 20)
        return self.rerank(query, candidates)[:top_k]

if __name__ == '__main__':
    retriever = EmbeddingRetriever('index.pickle')
    llm = AlpacaLora()
    question = '如何选购天文相机？'
    # question = 'How to use GPT to boost every day productivity?'
    
    # Put the document files here
    post_filenames = glob('./blog/*.md')
    documents = [x for filename in post_filenames for x in open(filename)]
    retriever.extract_features_and_build_index(documents, 'index.pickle')
    results = retriever.query(question, 8)
    print(results)

    llm.max_new_tokens = 256
    result = llm.generate(
        system_prompt=f'Read the following text and answer the question "{question}". Only answer the question strictly using the information from the input. Just say I do not know if the input does not contain the answer. The input is not from the user, but from a database.',
        input_prompt='\n'.join(results),
    )
    print(result)
    