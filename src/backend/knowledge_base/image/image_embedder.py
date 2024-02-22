import os

import numpy as np
import torch
from constants.env import CLIP_MODEL, CLIP_MODEL_CHN, MODEL_FOLDER
from loggers import img_embedder_logger as LOGGER
from PIL import Image
from torch import FloatTensor, Tensor
from transformers import (ChineseCLIPModel, ChineseCLIPProcessor, CLIPModel,
                          CLIPProcessor, CLIPTokenizer)
from transformers.models.clip.modeling_clip import CLIPOutput
from transformers.tokenization_utils_base import BatchEncoding


class ImageEmbedder:
    """It maintains multiple CLIP models for different languages, and provides functionalities to embed images and texts
    """

    def __init__(self):
        model_path: str = os.path.join(MODEL_FOLDER, CLIP_MODEL)
        model_path_cn: str = os.path.join(MODEL_FOLDER, CLIP_MODEL_CHN)

        LOGGER.info(f'Initializing image embedder, loading CLIP models...')
        # Use CLIP to embed images
        # - https://huggingface.co/docs/transformers/model_doc/clip
        self.encoder: CLIPProcessor = CLIPProcessor.from_pretrained(model_path)
        self.encoder_cn: ChineseCLIPProcessor = ChineseCLIPProcessor.from_pretrained(model_path_cn)
        self.model: CLIPModel = CLIPModel.from_pretrained(model_path)  # type: ignore
        self.tokenizer: CLIPTokenizer = CLIPTokenizer.from_pretrained(model_path)
        self.model_cn: ChineseCLIPModel = ChineseCLIPModel.from_pretrained(model_path_cn)  # type: ignore

    def __embed_image(self, img: Image.Image) -> np.ndarray:
        # The batch size is set to 1, so the first element of the output is the embedding of the image
        # - https://huggingface.co/transformers/model_doc/clip.html#clipmodel
        batch_size: int = 1

        # Encode image as input for CLIP model, to get features
        encoded: BatchEncoding = self.encoder(images=img, return_tensors="pt", padding=True)
        image_features: Tensor = self.model.get_image_features(encoded.get('pixel_values'))[batch_size - 1]
        feature: np.ndarray = image_features.numpy()
        return feature.astype(np.float32)

    def embed_image(self, img: Image.Image, use_grad: bool = False) -> np.ndarray:
        """Embed the given image
        - About use_grad(): https://datascience.stackexchange.com/questions/32651/what-is-the-use-of-torch-no-grad-in-pytorch
        """
        LOGGER.info('Embedding image with CLIP...')
        if not use_grad:
            with torch.no_grad():
                return self.__embed_image(img)
        else:
            return self.__embed_image(img)

    def embed_image_as_list(self, img: Image.Image, use_grad: bool = False) -> list[float]:
        """Embed an image and return vector as list
        """
        embedding: np.ndarray = self.embed_image(img, use_grad)
        return embedding.tolist()

    def embed_image_as_bytes(self, img: Image.Image, use_grad: bool = False) -> bytes:
        """Embed an image and return vector as bytes
        """
        embedding: np.ndarray = self.embed_image(img, use_grad)
        return embedding.tobytes()

    def embed_text(self, text: str, use_grad: bool = False) -> np.ndarray:
        """Embed the given text with CLIP model
        """
        LOGGER.info('Embedding text with CLIP...')
        encoded: BatchEncoding = self.encoder(text, return_tensors="pt", padding=True)
        text_features: FloatTensor = self.model.get_text_features(**encoded)  # type: ignore

        if not use_grad:
            with torch.no_grad():
                feature: np.ndarray = text_features.numpy()
        else:
            feature: np.ndarray = text_features.numpy()
        return feature.astype(np.float32)

    def compute_text_image_similarity(self, text_list: list[str], img: Image.Image) -> Tensor:
        """Query the given text and image against the CLIP model for similarity
        """
        LOGGER.info(f'Computing text-image similarity with CLIP for tokens: {text_list}', )

        # Use encoder to encode text+image as input for CLIP model, to get hybrid features
        encoded: BatchEncoding = self.encoder(text=text_list, images=img, return_tensors="pt", padding=True)
        # Unpack the batched encoding and feed it to the CLIP model directly to process both text and image
        image_features: CLIPOutput = self.model(**encoded)
        # Get the logits from the CLIP model
        return image_features.logits_per_image.softmax(dim=1)
