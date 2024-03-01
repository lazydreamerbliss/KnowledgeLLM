import os
from time import time

import numpy as np
import torch
import torch.amp.autocast_mode
import torchvision.transforms.functional as TVF
from constants.env import MODEL_FOLDER, TAGGER_MODEL
from knowledge_base.image.__tagger_model import TaggerModel
from loggers import img_embedder_logger as LOGGER
from PIL import Image
from torch import Tensor

TAG_FILE: str = 'top_tags.txt'


class ImageTagger:
    SCORE_THRESHOLD = 0.4

    def __init__(self, cuda: bool = False):
        model_path: str = os.path.join(MODEL_FOLDER, TAGGER_MODEL)
        self.device_type: str = 'cuda' if cuda else 'cpu'
        self.model: TaggerModel = TaggerModel.load_model(model_path)
        self.model.eval()
        self.model = self.model.to(self.device_type)

        self.tag_list: list[str] = list()
        self.tag_list_cn: list[str] = list()
        with open(os.path.join(model_path, TAG_FILE), 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                tag, tag_cn = line.split(':')
                self.tag_list.append(tag)
                self.tag_list_cn.append(tag_cn)

    def __embed_image(self, img: Image.Image) -> Tensor:
        # Pad image to square
        image_shape: tuple = img.size
        max_dim: int = max(image_shape)
        pad_left: int = (max_dim - image_shape[0]) // 2
        pad_top: int = (max_dim - image_shape[1]) // 2
        padded_image: Image.Image = Image.new('RGB', (max_dim, max_dim), (255, 255, 255))
        padded_image.paste(img, (pad_left, pad_top))

        # Resize image
        target_size: int = self.model.image_size
        if max_dim != target_size:
            padded_image = padded_image.resize((target_size, target_size), Image.BICUBIC)

        # Convert to tensor, then normalize with ImageNet mean and std
        image_features: Tensor = TVF.pil_to_tensor(padded_image) / 255.0
        image_features = TVF.normalize(image_features, mean=[0.48145466, 0.4578275, 0.40821073],
                                       std=[0.26862954, 0.26130258, 0.27577711])
        return image_features

    def __predict_tags(self, img: Image.Image, use_grad: bool = False) -> np.ndarray:
        image_features: Tensor = self.__embed_image(img)
        start: float = time()

        # Use autocast() and bfloat16 to speed up inference
        # - bfloat16 is a special float type for ML that is 2X faster than normal float32 and more accurate than float16
        with torch.amp.autocast_mode.autocast(self.device_type, dtype=torch.bfloat16, enabled=True):
            res: dict[str, Tensor] = self.model({'image': image_features.unsqueeze(0)})

        time_taken: float = time() - start
        LOGGER.info(f'Image tag predicted, cost: {time_taken:.2f}s')

        # Convert bfloat16 to float32 otherwise type conversion error will occur
        # - https://blog.csdn.net/caroline_wendy/article/details/132665807
        if not use_grad:
            with torch.no_grad():
                feature: np.ndarray = res['tags'].sigmoid().to(torch.float).cpu().numpy()
        else:
            feature: np.ndarray = res['tags'].sigmoid().to(torch.float).cpu().numpy()
        return feature.astype(np.float32)

    def get_tags(self, img: Image.Image, top_k: int = 10, en: bool = False) -> list[tuple[str, float]]:
        """Get top K tags for the given image

        Args:
            img (Image.Image): _description_
            top_k (int, optional): _description_. Defaults to 10.
            en (bool, optional): _description_. Defaults to False.

        Returns:
            list[tuple[str, float]]: _description_
        """
        LOGGER.info(f'Getting tags for image, top K: {top_k}, language: {"EN" if en else "CN"}')
        res: np.ndarray = self.__predict_tags(img)
        score_array: np.ndarray = res[0]
        from_tag_list: list[str] = self.tag_list if en else self.tag_list_cn

        # Item data type is np.float32, use item() to convert to native float
        # - https://stackoverflow.com/questions/9452775/converting-numpy-dtypes-to-native-python-types
        scores: dict[str, float] = {
            from_tag_list[i]: score_array[i].item()
            for i in range(len(from_tag_list)) if score_array[i] > ImageTagger.SCORE_THRESHOLD
        }
        sorted_top_k_scores: list[tuple[str, float]] = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return sorted_top_k_scores
