import time
from pathlib import Path

from PIL import Image

from knowledge_base.document.doc_embedder import DocEmbedder
from knowledge_base.image.image_embedder import ImageEmbedder
from knowledge_base.image.image_tagger import ImageTagger
from lib_manager import LibCreationObj
from library.document.doc_lib import DocumentLib
from library.document.doc_provider import DocProvider
from library.document.wechat.wechat_history_provider import \
    WechatHistoryProvider
from library.image.image_lib import ImageLib
from singleton import *
from utils.exceptions.lib_errors import LibraryManagerException


def test_doc_lib(doc_lib: DocumentLib):
    doc_lib.set_embedder(DocEmbedder())

    task_id: str = task_runner.submit_task(doc_lib.use_doc, None, True, True,
                                           relative_path='群聊_small.txt', provider_type=WechatHistoryProvider)
    while True:
        print(task_runner.get_task_state([task_id]))
        if task_runner.is_task_done(task_id):
            break
        time.sleep(1)

    res = doc_lib.query('哪家运营商可以开通公网ip？', 20, True)
    for i in res:
        print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    doc_lib.set_embedder(DocEmbedder())
    task_id: str = task_runner.submit_task(doc_lib.use_doc, None, True, True,
                                           relative_path='哈利波特.txt', provider_type=DocProvider)
    while True:
        print(task_runner.get_task_state([task_id]))
        if task_runner.is_task_done(task_id):
            break
        time.sleep(1)
    res = doc_lib.query('伏地魔附着在谁身上？', 20)
    for i in res:
        print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")


def test_image_lib(img_lib: ImageLib):
    img_lib.set_embedder(ImageEmbedder())
    task_id: str = task_runner.submit_task(img_lib.initialize, None, True, True, force_init=False)
    while True:
        print(task_runner.get_task_state([task_id]))
        if task_runner.is_task_done(task_id):
            break
        time.sleep(1)

    SAMPLE_FOLDER: str = f'{Path(__file__).parent.parent}/samples'
    test_img = Image.open(f"{SAMPLE_FOLDER}/1.jpg")
    a = img_lib.image_for_image_search(test_img, 2)
    print(a)
    b = img_lib.text_for_image_search('astronaut', 2)
    print(b)
    print("####################################")

    # sample_tagger = ImageTagger()
    # c = sample_tagger.get_tags(test_img, 10)
    # print(c)
    # print("####################################")


def test_llm():
    pass
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


def test_library_manager():
    TEST_DOC_LIB = '~/Documents/test_lib'
    TEST_IMG_LIB = '~/Pictures/test_lib'
    doc_lib_uuid = 'e8c0bd6f-2163-4294-92e6-4d225ab10b41'
    img_lib_uuid = '53821604-76a2-41b1-a655-e07a86096f93'

    doc_lib_creation = LibCreationObj()
    doc_lib_creation.type = 'document'
    doc_lib_creation.name = 'test_doc_lib'
    doc_lib_creation.uuid = doc_lib_uuid
    doc_lib_creation.path = TEST_DOC_LIB
    img_lib_creation = LibCreationObj()
    img_lib_creation.type = 'image'
    img_lib_creation.name = 'test_img_lib'
    img_lib_creation.uuid = img_lib_uuid
    img_lib_creation.path = TEST_IMG_LIB

    # Test library creation
    lib_manager.create_library(doc_lib_creation)
    lib_manager.create_library(img_lib_creation)

    # Test library switch
    lib_manager.use_library(doc_lib_uuid)
    doc_lib: DocumentLib = lib_manager.instance  # type: ignore
    test_doc_lib(doc_lib)
    # Test library switch
    lib_manager.use_library(img_lib_uuid)
    img_lib: ImageLib = lib_manager.instance  # type: ignore
    test_image_lib(img_lib)

    # Test library demolish
    lib_manager.use_library(doc_lib_uuid)
    lib_manager.demolish_library()
    lib_manager.use_library(img_lib_uuid)
    lib_manager.demolish_library()

    # Test library creation again
    lib_manager.create_library(doc_lib_creation)
    lib_manager.create_library(img_lib_creation)

    # Test library switch again
    lib_manager.use_library(doc_lib_uuid)
    doc_lib: DocumentLib = lib_manager.instance  # type: ignore
    test_doc_lib(doc_lib)
    # Test library switch again
    lib_manager.use_library(img_lib_uuid)
    img_lib: ImageLib = lib_manager.instance  # type: ignore
    test_image_lib(img_lib)


if __name__ == '__main__':
    test_library_manager()
    test_llm()
