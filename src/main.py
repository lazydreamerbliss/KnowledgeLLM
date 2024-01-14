import argparse
from pathlib import Path

from PIL import Image

from image_knowledge.image_lib import ImageLib
from image_knowledge.image_tagger import ImageTagger
from server.server import flask_app
from singleton import img_embedder


def run_server():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-P", type=int, default=5000, help="Listening port (default: 5000)")
    parser.add_argument("--host", "-H", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--debug", "-D", default=False, required=False, action="store_true",
                        help="True when argument is provided for debug")
    args = parser.parse_args()

    # asyncio.run(task_queue.run())

    debug: bool = args.debug
    host: str = args.host
    port: int = args.port
    flask_app.run(host=host, port=port, debug=debug, threaded=True)


def run_test():
    # doc test
    # test_doc_embedder = DocEmbedder('test_index.pickle')
    # test_doc_embedder.initialize('test_index.pickle', 'test_chat',
    #                              '/Users/chengjia/Documents/WechatDatabase/Seventh_Seal/群聊.txt')
    # res = test_doc_embedder.query('哪家运营商可以开通公网ip？', 20, True)
    # for i in res:
    #     print(i)

    SAMPLE_FOLDER: str = f'{Path(__file__).parent.parent}/samples'
    test_img = Image.open(f"{SAMPLE_FOLDER}/1.jpg")

    lib_mem = ImageLib(img_embedder, '~/Pictures/test_set_mem', 'testlib', force_init=False, local_mode=True)
    a = lib_mem.image_for_image_search(test_img, 2)
    print(a)
    b = lib_mem.text_for_image_search('astronaut', 2)
    print(b)
    lib_mem.scan_lib()

    lib_redis = ImageLib(img_embedder, '~/Pictures/test_set_redis', 'testlib', force_init=False, local_mode=False)
    a = lib_redis.image_for_image_search(test_img, 2)
    print(a)
    b = lib_redis.text_for_image_search('astronaut', 2)
    print(b)
    lib_redis.scan_lib()

    sample_tagger = ImageTagger()
    c = sample_tagger.get_tags(test_img, 10)
    print(c)

    # # Prepare raw documents
    # post_filenames: list[str] = glokeys *b('. /blog/*.md')
    # documents: list[str] = [x for filename in post_filenames for x in open(filename)]
    #
    # # Initialize retriever
    # retriever = EmbeddingRetriever('index.pickle')
    # retriever.extract_features_and_build_index(documents, 'index.pickle')
    #
    # # Query
    # question: str = '如何选购天文相机？'
    # candidates: list[str] = retriever.query(question, 8)
    #
    # # Generate answer using with LLM
    # llm = AlpacaLora()
    # llm.max_new_tokens = 256
    # result = llm.generate(
    #     system_prompt=f'Read the following text and answer this question: "{question}".'
    #                   f'Only answer the question strictly using the information from the input.'
    #                   f'The input is not from the user, but from a database.'
    #                   f'Just say I do not know if the input does not contain the answer.'
    #                   f'Please use Chinese to answer everything.',
    #     input_prompt='\n'.join(candidates)
    # )


if __name__ == '__main__':
    run_server()
else:
    # Run with gunicorn
    # - See docker-compose.prod.yml `gunicorn --bind 0.0.0.0:5000 main:gunicorn_app`
    # - doc: https://docs.gunicorn.org/en/stable/run.html
    gunicorn_app = flask_app
