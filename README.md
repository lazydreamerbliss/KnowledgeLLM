# Knowledge Ingestion for LLM

This project offers a reference implementation that combines document retrieval with a large language model like Llama, allowing users to ask questions and receive answers based on a knowledge base. You can also replace the large language model inference with OpenAI APIs for even better performance. 
- It supports both In-Memory and Redis-based vector DB, depends on your configuration
- If In-Memory vector DB is used, then no Redis is needed and this application is a stand-alone app

## Install backend requirements
(Python 3.10+) `pip install -r requirements.txt`
- `torch` needs to be installed manually from https://pytorch.org/get-started/locally/, depends on local hardware

## Downlod model pack
There are two options to use the models:
1. Use default path and let HuggingFace download them for you, they will be stored in `~/.cache/huggingface/hub/`
2. Manually download models, and provde the model folder in configuration
  - TODO: provide model download guide

## Run the dev server from code
- Dev mode: edit and run `main.py` directly from terminal by `python main.py [--port 5012] [--host 0.0.0.0] [--debug True]`
  - (Optional) `port` is defaulted by `5000`
  - (Optional) `host` is defaulted to `localhost`
  - (Optional) `debug` is defaulted to `False`, enabling debug will enable hot-reload but it will also slow down the program

## Run dev server with redis - Redis only
You need to edit the docker-compose file for your own volume path for test
1. Run dev server from terminal
2. Run redis docker-compose file by execute `bash run.dev.redis.sh`

## Run dev server with redis - All in docker
You need to edit the docker-compose file for your own volume path for test
1. Run server+redis docker-compose file by execute `bash run.dev.sh`
