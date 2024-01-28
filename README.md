# Knowledge Ingestion for LLM

This project offers a reference implementation that combines document retrieval with a large language model like Llama, allowing users to ask questions and receive answers based on a knowledge base. You can also replace the large language model inference with OpenAI APIs for even better performance. 
- It supports both In-Memory and Redis-based vector DB, depends on your configuration
- If In-Memory vector DB is used, then no Redis is needed and this application is a stand-alone app

On the main page of the app (after started the local server), simply pick a folder a your knowledge library, and ask questions to it!
- Navigate your knowledge library in different view styles and image gallery mode
- Initialize your knowledge library into embeddings, and:
  - Text serch for your document library
  - Image/Text to image search for your image library
  - Ask AI assistent about anything in your library (under development)

## Current progress
- Orchestrating on Electron, deprecating python server
- Tuning document knowledge base
  - Supporting more document types such as docx, pdf, etc.
- Improve image knowledge base's performance

### TODO
- Video knowledge base

## Install requirements
(Python 3.10+) `pip install -r requirements.txt`
- `torch` needs to be installed manually from https://pytorch.org/get-started/locally/, depends on local hardware

### Downlod model pack
There are two options to use the models:
1. Use default path and let HuggingFace download them for you, they will be stored in `~/.cache/huggingface/hub/`
2. Manually download models, and provide the model folder in configuration
  - TODO: provide model pack for manual download

## Test knowledge base from terminal
Two knowledge bases are currently supported:
- Document
- Image

To test knowledge base from terminal directly, you can try following code:
```python
# Create a task runner, this is optional
task_runner: TaskRunner = TaskRunner()

# Provide a UUID for your knowledge base, this cannot be changed after the library is created
uuid: str = 'e8c0bd6f-2163-4294-92e6-4d225ab10b41'
# This will instanize a document library, and it cannot be used until one of the document under this library is activated
doc_lib: DocumentLib = DocumentLib(PATH_TO_LIB, NAME_OF_LIB, uuid)
doc_lib.set_embedder(DocEmbedder())

# You can either activate a document sync, or in background (with task runner)
# - Use WechatHistoryProvider for parsing wechat history
# - Use DocProvider for parsing general document like txt
#
# To activate a document sync, as below:
doc_lib.use_doc(relative_path=RELATIVE_PATH_TO_DOC, provider_type=DocProvider)
# Or to activate a document async, and acquire the task's execution status:
task_id: str = task_runner.submit_task(doc_lib.use_doc, None, True, True,
                                       relative_path=RELATIVE_PATH_TO_DOC, provider_type=DocProvider)
while True:
    print(task_runner.get_task_state([task_id]))
    if task_runner.is_task_done(task_id):
        break

# Go ask a question!
res = doc_lib.query(QUESTION, 20, True)
```

To test knowledge base for image, it is easier:
```python
# Provide a UUID for your knowledge base, this cannot be changed after the library is created
uuid = '53821604-76a2-41b1-a655-e07a86096f93'
# This will instanize an image library, and it cannot be used until it is initialized (library scan)
# - You can choose to use Redis or In-Memory DB at your will, if local_mode=False then Redis is mandatory
img_lib = ImageLib(PATH_TO_LIB, NAME_OF_LIB, uuid, local_mode=True)
img_lib.set_embedder(ImageEmbedder())

# Same as document library, initialization can be sync or async:
img_lib.initialize(force_init=True)
# Or:
task_id: str = task_runner.submit_task(img_lib.initialize, None, True, True, force_init=True)
while True:
    print(task_runner.get_task_state([task_id]))
    if task_runner.is_task_done(task_id):
        break

# Go search your image with image or text!
res = img_lib1.image_for_image_search(TEST_IMAGE, 2)
res = img_lib1.text_for_image_search('astronaut', 2)
```

## Run the dev server for UI (under deprecating)
- Dev mode: edit and run `main.py` directly from terminal by `python main.py [--port 5012] [--host 0.0.0.0] [--debug True]`
  - (Optional) `port` is defaulted by `5000`
  - (Optional) `host` is defaulted to `localhost`
  - (Optional) `debug` is defaulted to `False`, enabling debug will enable hot-reload but it will also slow down the program

### With redis - Redis only
You need to edit the docker-compose file for your own volume path for test
1. Run dev server from terminal
2. Run redis docker-compose file by execute `bash run.dev.redis.sh`

### With redis - All in docker
You need to edit the docker-compose file for your own volume path for test
1. Run server+redis docker-compose file by execute `bash run.dev.sh`

