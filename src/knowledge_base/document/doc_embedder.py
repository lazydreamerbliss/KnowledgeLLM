import os
from pathlib import Path

import numpy as np
import numpy.typing as npt
import torch
from sentence_transformers import CrossEncoder, SentenceTransformer
from transformers import BertModel, BertTokenizer
from transformers.tokenization_utils_base import BatchEncoding

from utils.tqdm_context import TqdmContext

MODEL_FOLDER: str = f'{Path(__file__).parent.parent.parent.parent}/local_models'
TRANSFORMER_NAME: str = 'shibing624_text2vec-base-chinese'
CROSS_ENCODER_NAME: str = 'hfl--chinese-roberta-wwm-ext'


class DocEmbedder:
    def __init__(self):
        transformer_path: str = os.path.join(MODEL_FOLDER, 'sentence_transformers',  TRANSFORMER_NAME)
        cross_encoder_path: str = os.path.join(MODEL_FOLDER, CROSS_ENCODER_NAME)

        with TqdmContext('Initializing text embedder, loading transformers...', 'Loaded'):
            self.transformer: SentenceTransformer = SentenceTransformer(transformer_path)
            self.tokenizer: BertTokenizer = BertTokenizer.from_pretrained(cross_encoder_path)
            self.model: BertModel = BertModel.from_pretrained(cross_encoder_path)  # type: ignore

            # Set the model to evaluation mode to deactivate training dropout
            self.model.eval()  # type: ignore

    def embed_text(self, text: str, use_grad: bool = False) -> np.ndarray:
        if not use_grad:
            with torch.no_grad():
                feature: np.ndarray = self.transformer.encode(text)  # type: ignore
        else:
            feature: np.ndarray = self.transformer.encode(text)  # type: ignore
        return feature.astype(np.float32)

    def predict_similarity(self, goal: str, candidate: str, use_grad: bool = False) -> npt.ArrayLike:
        # CrossEncoder.predict() accepts a 2D matrix as input for similarity analysis
        # - Each row of the matrix is a sample to be predicted, the first element of each row is the query text (source text), the second element is the document retrieved (target text)
        # - It returns a 1D matrix, each element is the prediction score (percentage) for the current text + doc (higher score is more relevant in semantics)
        # - https://aistudio.baidu.com/projectdetail/4951278
        texts = [
            'Obama speaks to the media in Illinois',
            'The president greets the press in Chicago',
            'Oranges are my favorite fruit',
        ]

        # Use tokenizer to encode text as input for BERT model, to get features
        encoded: BatchEncoding = self.tokenizer(
            texts,  # the texts to be tokenized
            padding=True,  # pad the texts to the maximum length (so that all outputs have the same length)
            return_tensors='pt'  # return the tensors (not lists)
        )

        if not use_grad:
            with torch.no_grad():
                feature: np.ndarray = self.model(**encoded)
        else:
            feature: np.ndarray = self.model(**encoded)

        # if not goal or not candidate:
        #     return 0
        # return self.ranker.predict([[goal, candidate]])

    def predict_similarity_batch(self, goal: str, candidates: list[str], use_grad: bool = False) -> npt.ArrayLike:
        # if not goal or not candidates:
        #     return list()

        # merged: list[list[str]] = [[goal, candidate] for candidate in candidates]
        # return self.ranker.predict(merged)
        pass
