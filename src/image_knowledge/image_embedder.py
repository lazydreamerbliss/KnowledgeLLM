from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import FloatTensor, Tensor
from transformers import (ChineseCLIPModel, ChineseCLIPProcessor, CLIPModel,
                          CLIPProcessor, CLIPTokenizer)
from transformers.models.clip.modeling_clip import CLIPOutput
from transformers.tokenization_utils_base import BatchEncoding

from utils.tqdm_context import TqdmContext


class ImageEmbedder:
    """It maintains multiple CLIP models for different languages, and provides functionalities to embed images and texts
    """
    # Model folder: ../../../local_models/...
    MODEL_FOLDER: str = f'{Path(__file__).parent.parent.parent}/local_models'
    model_path: str = f'{MODEL_FOLDER}/openai--clip-vit-base-patch16/snapshots/57c216476eefef5ab752ec549e440a49ae4ae5f3'
    model_path_cn: str = f'{MODEL_FOLDER}/OFA-Sys--chinese-clip-vit-base-patch16/snapshots/36e679e65c2a2fead755ae21162091293ad37834'

    def __init__(self):
        with TqdmContext('Initializing embedder, loading CLIP models...', 'Loaded'):
            # Use CLIP to embed images
            # - https://huggingface.co/docs/transformers/model_doc/clip
            self.processor: CLIPProcessor = CLIPProcessor.from_pretrained(ImageEmbedder.model_path)
            self.model: CLIPModel = CLIPModel.from_pretrained(ImageEmbedder.model_path)  # type: ignore
            self.tokenizer: CLIPTokenizer = CLIPTokenizer.from_pretrained(ImageEmbedder.model_path)
            self.model_cn: ChineseCLIPModel = ChineseCLIPModel.from_pretrained(
                ImageEmbedder.model_path_cn)  # type: ignore
            self.processor_cn: ChineseCLIPProcessor = ChineseCLIPProcessor.from_pretrained(ImageEmbedder.model_path_cn)

    def __embed_image(self, img: Image.Image) -> np.ndarray:
        # The batch size is set to 1, so the first element of the output is the embedding of the image
        # - https://huggingface.co/transformers/model_doc/clip.html#clipmodel
        batch_size: int = 1

        # Use processor to build input data for CLIP model, and use model to get image features
        clip_input: BatchEncoding = self.processor(images=img, return_tensors="pt", padding=True)
        image_features: Tensor = self.model.get_image_features(clip_input.get('pixel_values'))[batch_size-1]
        return image_features.numpy().astype(np.float32)

    def embed_image(self, img: Image.Image, use_grad: bool = False) -> np.ndarray:
        """Embed the given image
        - About use_grad(): https://datascience.stackexchange.com/questions/32651/what-is-the-use-of-torch-no-grad-in-pytorch
        """
        if not use_grad:
            with torch.no_grad():
                return self.__embed_image(img)
        else:
            return self.__embed_image(img)

    def embed_image_as_list(self, img: Image.Image, use_grad: bool = False) -> list[float]:
        """Embed an image and return vector as list
        """
        embeddings: np.ndarray = self.embed_image(img, use_grad)
        return embeddings.tolist()

    def embed_image_as_bytes(self, img: Image.Image, use_grad: bool = False) -> bytes:
        """Embed an image and return vector as bytes
        """
        embeddings: np.ndarray = self.embed_image(img, use_grad)
        return embeddings.tobytes()

    def embed_text(self, text: str, use_grad: bool = False) -> np.ndarray:
        """Embed the given text
        """
        inputs: BatchEncoding = self.processor(text, return_tensors="pt", padding=True)
        text_features: FloatTensor = self.model.get_text_features(**inputs)  # type: ignore

        if not use_grad:
            with torch.no_grad():
                return text_features.numpy().astype(np.float32)
        return text_features.numpy().astype(np.float32)

    def compute_text_image_similarity(self, text_list: list[str], img: Image.Image) -> Tensor:
        """Query the given text and image against the CLIP model for similarity
        """
        # Use processor to build input data for CLIP model, with both text and image functionalities
        clip_input: BatchEncoding = self.processor(text=text_list, images=img, return_tensors="pt", padding=True)
        # Unpack the batched encoding and feed it to the CLIP model directly to process both text and image
        image_features: CLIPOutput = self.model(**clip_input)
        # Get the logits from the CLIP model
        return image_features.logits_per_image.softmax(dim=1)
