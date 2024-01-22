import os
from pathlib import Path

import numpy.typing as npt
from sentence_transformers import CrossEncoder, SentenceTransformer

from utils.tqdm_context import TqdmContext


class DocEmbedder:
    # Model folder: ../../../local_models/...
    MODEL_FOLDER: str = f'{Path(__file__).parent.parent.parent.parent}/local_models'
    transformer_path: str = os.path.join(MODEL_FOLDER, 'sentence_transformers', 'shibing624_text2vec-base-chinese')
    # "cross-encoder/ms-marco-MiniLM-L-12-v2": re-rank a list of candidate by their semantic similarity (https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-12-v2)
    cross_encoder_path: str = os.path.join(MODEL_FOLDER, 'hfl--chinese-roberta-wwm-ext', 'snapshots', '5c58d0b8ec1d9014354d691c538661bf00bfdb44')

    def __init__(self):
        with TqdmContext('Initializing text embedder, loading transformers...', 'Loaded'):
            self.transformer: SentenceTransformer = SentenceTransformer(DocEmbedder.transformer_path)
            self.ranker: CrossEncoder = CrossEncoder(DocEmbedder.cross_encoder_path, max_length=512)

    def embed_text(self, text: str) -> npt.ArrayLike:
        return self.transformer.encode(text)

    def predict_similarity(self, goal: str, candidate: str) -> npt.ArrayLike:
        # CrossEncoder.predict() accepts a 2D matrix as input for similarity analysis
        # - Each row of the matrix is a sample to be predicted, the first element of each row is the query text (source text), the second element is the document retrieved (target text)
        # - It returns a 1D matrix, each element is the prediction score (percentage) for the current text + doc (higher score is more relevant in semantics)
        # - https://aistudio.baidu.com/projectdetail/4951278
        if not goal or not candidate:
            return 0
        return self.ranker.predict([[goal, candidate]])

    def predict_similarity_batch(self, goal: str, candidates: list[str]) -> npt.ArrayLike:
        if not goal or not candidates:
            return list()

        merged: list[list[str]] = [[goal, candidate] for candidate in candidates]
        return self.ranker.predict(merged)
