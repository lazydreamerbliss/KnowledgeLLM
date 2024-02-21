import time
from pathlib import Path

from knowledge_base.image.image_tagger import ImageTagger
from library.document.doc_lib import DocumentLib
from library.document.doc_provider import DocProvider
from library.document.wechat.wechat_history_provider import \
    WechatHistoryProvider
from library.image.image_lib import ImageLib
from PIL import Image
from singleton import *
from utils.lib_manager import LibInfo

TEST_DOC_LIB = '~/Documents/test_lib'
TEST_IMG_LIB = '~/Pictures/test_lib'
SAMPLE_FOLDER: str = f'{Path(__file__).parent.parent}/samples'

DOC_LIB_UUID = 'e8c0bd6f-2163-4294-92e6-4d225ab10b41'
IMG_LIB_UUID = '53821604-76a2-41b1-a655-e07a86096f93'


def test_doc_lib(lib_manager: LibraryManager):
    lib_manager.use_library(DOC_LIB_UUID)
    doc_lib: DocumentLib = lib_manager.instance  # type: ignore

    # task_id: str | None = lib_manager.get_ready(relative_path='群聊_small.txt', provider_type=WechatHistoryProvider, lite_mode=False)
    # while True:
    #     if not task_id or task_runner.is_task_done(task_id):
    #         print(task_runner.get_task_state(task_id))  # type: ignore
    #         break
    #     else:
    #         print(task_runner.get_task_state(task_id))  # type: ignore
    #     time.sleep(1)

    # if task_id and not task_runner.is_task_successful(task_id):
    #     # Failed to load the document
    #     return
    # res = doc_lib.query('女士健身房', 20, False)
    # for i in res:
    #     print(i)
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # res = doc_lib.query('女士健身房', 20, True)
    # for i in res:
    #     print(i)
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    task_id: str | None = lib_manager.make_library_ready(relative_path='哈利波特.txt', provider_type=DocProvider)
    while True:
        if not task_id or task_runner.is_task_done(task_id):
            print(task_runner.get_task_state(task_id))  # type: ignore
            break
        else:
            print(task_runner.get_task_state(task_id))  # type: ignore
        time.sleep(1)

    if task_id and not task_runner.is_task_successful(task_id):
        # Failed to load the document
        return

    res = doc_lib.query('伏地魔附着在谁身上？', 20)
    for i in res:
        print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    task_id: str | None = lib_manager.make_library_ready(relative_path='哈利波特.docx', provider_type=DocProvider)
    while True:
        if not task_id or task_runner.is_task_done(task_id):
            print(task_runner.get_task_state(task_id))  # type: ignore
            break
        else:
            print(task_runner.get_task_state(task_id))  # type: ignore
        time.sleep(1)

    if task_id and not task_runner.is_task_successful(task_id):
        # Failed to load the document
        return

    res = doc_lib.query('伏地魔附着在谁身上？', 20)
    for i in res:
        print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    task_id: str | None = lib_manager.make_library_ready(relative_path='哈利波特.pdf', provider_type=DocProvider)
    while True:
        if not task_id or task_runner.is_task_done(task_id):
            print(task_runner.get_task_state(task_id))  # type: ignore
            break
        else:
            print(task_runner.get_task_state(task_id))  # type: ignore
        time.sleep(1)

    if task_id and not task_runner.is_task_successful(task_id):
        # Failed to load the document
        return

    res = doc_lib.query('伏地魔附着在谁身上？', 20)
    for i in res:
        print(i)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")


def test_image_lib(lib_manager: LibraryManager, test_lib_manager: bool):
    if lib_manager.use_library(IMG_LIB_UUID):
        img_lib: ImageLib = lib_manager.instance  # type: ignore
        if test_lib_manager:
            task_id: str | None = lib_manager.make_library_ready()
            while True:
                if not task_id or task_runner.is_task_done(task_id):
                    print(task_runner.get_task_state(task_id))  # type: ignore
                    break
                else:
                    print(task_runner.get_task_state(task_id))  # type: ignore
                time.sleep(1)

            if task_id and not task_runner.is_task_successful(task_id):
                # Failed to load the document
                return
        else:
            img_lib.set_embedder(ImageEmbedder())
            img_lib.full_scan()
            img_lib.incremental_scan()

        for i in img_lib.get_embedded_files().keys():
            print(i, img_lib.get_embedded_files()[i])

        test_img = Image.open(f"{SAMPLE_FOLDER}/1.jpg")
        a = img_lib.image_for_image_search(test_img, 2)
        print(a)
        print("####################################")
        b = img_lib.text_for_image_search('astronaut', 2)
        print(b)
        print("####################################")

        sample_tagger = ImageTagger()
        c = sample_tagger.get_tags(test_img, 10)
        print(c)
        print("####################################")


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
    doc_lib_creation = LibInfo()
    doc_lib_creation.type = 'document'
    doc_lib_creation.name = 'test_doc_lib'
    doc_lib_creation.uuid = DOC_LIB_UUID
    doc_lib_creation.path = TEST_DOC_LIB
    img_lib_creation = LibInfo()
    img_lib_creation.type = 'image'
    img_lib_creation.name = 'test_img_lib'
    img_lib_creation.uuid = IMG_LIB_UUID
    img_lib_creation.path = TEST_IMG_LIB

    # Test library creation
    lib_manager.create_library(doc_lib_creation)
    lib_manager.create_library(img_lib_creation)

    # Test library switch - doc
    test_doc_lib(lib_manager)
    # Test library switch - image
    # test_image_lib(lib_manager, True)

    # # Test library demolish
    # lib_manager.use_library(DOC_LIB_UUID)
    # lib_manager.demolish_library()
    # lib_manager.use_library(IMG_LIB_UUID)
    # lib_manager.demolish_library()

    # # Test library creation again
    # lib_manager.create_library(doc_lib_creation)
    # lib_manager.create_library(img_lib_creation)

    # # Test library switch - doc again
    # test_doc_lib(lib_manager)
    # # Test library switch - image again
    # test_image_lib(lib_manager)


if __name__ == '__main__':
    test_library_manager()

    # bb = DocEmbedder()
    # print(bb.predict_similarity('女士健身房', '女士健身房'))
    # print(bb.predict_similarity('女士健身房', '这是女士健身房吗'))
    # print(bb.predict_similarity('女士健身房', '这是女士健身房吗？'))
    # print(bb.predict_similarity('女士健身房', '不是的，男生在后面没有拍到 这是女士健身房吗？'))
    # print(bb.predict_similarity('女士健身房', '好的'))
    # print(bb.predict_similarity('女士健身房', '我用过类似方案，省硬盘钱。后来想了想没必要公网，集团撤了，稳的问题，可以用域名负载来解决问题'))
    # print(bb.predict_similarity('The president is arriving to east coast', 'Obama is giving speech in Florida'))
    # print(bb.predict_similarity('总统先生即将到达东海岸', '奥巴马总统正在佛罗里达演讲'))
    # print(bb.predict_similarity('今天天气不错', '今天心情不错'))
