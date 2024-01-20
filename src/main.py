import argparse
from pathlib import Path

from PIL import Image

from knowledge_base.image.image_tagger import ImageTagger
from library.document.doc_lib import DocLib
from library.document.doc_provider import DocProvider
from library.document.wechat.wechat_history_provider import \
    WechatHistoryProvider
from library.image.image_lib import ImageLib
from server.server import flask_app
from singleton import doc_embedder, img_embedder


def run_server():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-P", type=int, default=5000, help="Listening port (default: 5000)")
    parser.add_argument("--host", "-H", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--debug", "-D", default=False, required=False, action="store_true",
                        help="True when argument is provided for debug")
    args = parser.parse_args()

    debug: bool = args.debug
    host: str = args.host
    port: int = args.port
    flask_app.run(host=host, port=port, debug=debug, threaded=True)


def library_test():
    doc_lib = DocLib(doc_embedder, '~/Documents/test_lib', 'doc_lib_test')
    # doc_lib.initialize_doc('群聊_small.txt', WechatHistoryProvider)
    # res = doc_lib.query('哪家运营商可以开通公网ip？', 20, True)
    # for i in res:
    #     print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    doc_lib.initialize_doc('哈利波特.txt', DocProvider)
    res = doc_lib.query('伏地魔附着在谁身上？', 20)
    for i in res:
        print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    doc_lib.switch_doc('群聊_small.txt', WechatHistoryProvider)
    res = doc_lib.query('哪家运营商可以开通公网ip？', 20)
    for i in res:
        print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    doc_lib.switch_doc('哈利波特.txt', DocProvider)
    res = doc_lib.query('伏地魔附着在谁身上？', 20)
    for i in res:
        print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    SAMPLE_FOLDER: str = f'{Path(__file__).parent.parent}/samples'
    test_img = Image.open(f"{SAMPLE_FOLDER}/1.jpg")

    img_lib1 = ImageLib(img_embedder, '~/Pictures/test_lib', 'testlib', force_init=False, local_mode=True)
    a = img_lib1.image_for_image_search(test_img, 2)
    print(a)
    b = img_lib1.text_for_image_search('astronaut', 2)
    print(b)
    print("####################################")

    # img_lib2_redis = ImageLib(img_embedder, '~/Pictures/test_lib', 'testlib', force_init=False, local_mode=False)
    # a = img_lib2_redis.image_for_image_search(test_img, 2)
    # print(a)
    # b = img_lib2_redis.text_for_image_search('astronaut', 2)
    # print(b)
    # print("####################################")

    sample_tagger = ImageTagger()
    c = sample_tagger.get_tags(test_img, 10)
    print(c)
    print("####################################")

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
    library_test()
    # run_server()
else:
    # Run with gunicorn
    # - See docker-compose.prod.yml `gunicorn --bind 0.0.0.0:5000 main:gunicorn_app`
    # - doc: https://docs.gunicorn.org/en/stable/run.html
    gunicorn_app = flask_app
