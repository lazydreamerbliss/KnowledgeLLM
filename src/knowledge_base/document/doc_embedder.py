import os

import numpy as np
import numpy.typing as npt
import torch
from sentence_transformers import CrossEncoder, SentenceTransformer, util
from torch import Tensor

from env import CROSS_ENCODER_MODEL, MODEL_FOLDER, TRANSFORMER_MODEL
from utils.tqdm_context import TqdmContext


class DocEmbedder:
    def __init__(self, lite_mode: bool = False):
        transformer_path: str = os.path.join(MODEL_FOLDER, 'sentence_transformers',  TRANSFORMER_MODEL)
        cross_encoder_path: str = os.path.join(MODEL_FOLDER, CROSS_ENCODER_MODEL)

        with TqdmContext('Initializing text embedder, loading transformers...', 'Loaded'):
            self.transformer: SentenceTransformer = SentenceTransformer(transformer_path)
            self.cross_encoder: CrossEncoder | None = None
            # Lite mode will use transformer only (no cross-encoder) for all purposes, to reduce total model size
            if not lite_mode and os.path.isdir(cross_encoder_path):
                self.cross_encoder = CrossEncoder(cross_encoder_path, max_length=512)

    def embed_text(self, text: str, use_grad: bool = False) -> np.ndarray:
        if not use_grad:
            with torch.no_grad():
                feature: np.ndarray = self.transformer.encode(text)  # type: ignore
        else:
            feature: np.ndarray = self.transformer.encode(text)  # type: ignore
        return feature.astype(np.float32)

    def predict_similarity(self, goal: str, candidate: str, use_grad: bool = False) -> npt.ArrayLike:
        # Lite mode - use transformer for all purposes and calculate cosine similarity between two embeddings directly
        if not self.cross_encoder:
            if not use_grad:
                with torch.no_grad():
                    g_feature: Tensor = self.transformer.encode(goal, convert_to_tensor=True)  # type: ignore
                    c_feature: Tensor = self.transformer.encode(candidate, convert_to_tensor=True)  # type: ignore
            else:
                g_feature: Tensor = self.transformer.encode(goal, convert_to_tensor=True)  # type: ignore
                c_feature: Tensor = self.transformer.encode(candidate, convert_to_tensor=True)  # type: ignore

            res: Tensor = util.pytorch_cos_sim(g_feature, c_feature)
            return res.numpy().item()

        # CrossEncoder mode
        #
        # CrossEncoder.predict() accepts a 2D matrix as input for similarity analysis
        # - Each row of the matrix is a sample to be predicted, the first element of each row is the query text (source text), the second element is the document retrieved (target text)
        # - It returns a 1D matrix, each element is the prediction score (percentage) for the current text + doc (higher score is more relevant in semantics)
        # - https://aistudio.baidu.com/projectdetail/4951278
        if not goal or not candidate:
            return 0
        return self.cross_encoder.predict([[goal, candidate]])

    def predict_similarity_batch(self, goal: str, candidates: list[str], use_grad: bool = False) -> npt.ArrayLike:
        if not goal or not candidates:
            return list()

        # Lite mode
        if not self.cross_encoder:
            if not use_grad:
                with torch.no_grad():
                    g_feature: Tensor = self.transformer.encode(goal, convert_to_tensor=True)  # type: ignore
                    c_features: list[Tensor] = self.transformer.encode(
                        candidates, convert_to_tensor=True)  # type: ignore
            else:
                g_feature: Tensor = self.transformer.encode(goal, convert_to_tensor=True)  # type: ignore
                c_features: list[Tensor] = self.transformer.encode(candidates, convert_to_tensor=True)  # type: ignore
            return [util.pytorch_cos_sim(g_feature, c_feature).numpy().item() for c_feature in c_features]

        # CrossEncoder mode
        merged: list[list[str]] = [[goal, candidate] for candidate in candidates]
        return self.cross_encoder.predict(merged)
