import os
import sys
from pathlib import Path

import torch
from utils.containable_enum import ContainableEnum


class Environment(ContainableEnum):
    PROD = 'PROD'
    DEV = 'DEV'


# Environment
ENV: str | None = os.environ.get("ENV", None)
if not ENV or ENV not in Environment:
    ENV = Environment.DEV.name

# Device and OS
DEVICE: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
IS_WINDOWS: bool = 'win32' in sys.platform or 'win64' in sys.platform
IS_LINUX: bool = 'linux' in sys.platform
IS_OSX: bool = 'darwin' in sys.platform

# gRPC port
GRPC_PORT: int = int(os.environ.get('GRPC_PORT', 50051))

# Model info
# - TODO: Change folders to installation path
MODEL_FOLDER: str = f'{Path(__file__).parent.parent.parent.parent}/local_models'
CLIP_MODEL: str = 'openai--clip-vit-base-patch16'
CLIP_MODEL_CHN: str = 'OFA-Sys--chinese-clip-vit-base-patch16'
TRANSFORMER_MODEL: str = 'shibing624_text2vec-base-chinese-sentence'
BERT_MODEL: str = 'hfl--chinese-roberta-wwm-ext'
CROSS_ENCODER_MODEL: str = 'tuhailong--cross_encoder_roberta-wwm-ext_v2'
TAGGER_MODEL: str = 'fancyfeast--joytag'

# Config folder, logging folder, etc.
# - TODO: Change folders to installation path
CONFIG_FOLDER: str = f'{Path(__file__).parent.parent.parent.parent}'
LOGGING_FOLDER: str = f'{Path(__file__).parent.parent.parent.parent}/logs'

REDIS_HOST: str = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PWD: str = os.environ.get('REDIS_PWD', 'test123')
REDIS_PORT: int = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DATA_DIR: str = os.environ.get('REDIS_DATA_DIR', '/data')
