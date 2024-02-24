import importlib
import time
from types import ModuleType

import grpc
from constants.env import GRPC_PORT
from loggers import logger as TEST_LOGGER
from PIL import Image
from server.grpc.backend_pb2_grpc import GrpcServerStub
from server.grpc.obj_basic_pb2 import *
from server.grpc.obj_shared_pb2 import *
from server.grpc_server import GrpcServer
from tests.lib_info import *
from utils.file_helper import open_image_as_base64
from utils.lib_manager import LibraryManager
from utils.task_runner import TaskRunner

task_runner: TaskRunner = TaskRunner()
test_server: GrpcServer = GrpcServer(task_runner, LibraryManager(task_runner))
doc_provider: ModuleType = importlib.import_module('library.document.doc_provider')
wechat_history_provider: ModuleType = importlib.import_module('library.document.wechat.wechat_history_provider')


class GrpcClientForServerTest:
    def __init__(self, address: str = f'localhost:{GRPC_PORT}'):
        self.stub: GrpcServerStub = GrpcServerStub(grpc.insecure_channel(address))

    def test_heartbeat(self):
        response = self.stub.heartbeat(VoidObj())
        print(response)

    def test_create_library(self, lib_info: LibInfo):
        # Create library
        request = LibInfoObj()
        request.name = lib_info.name
        request.uuid = lib_info.uuid
        request.path = lib_info.path
        request.type = lib_info.type
        res: BooleanObj = self.stub.create_library(request)
        assert res.value, True

    def test_switch_to_library(self, uuid: str, expected: bool):
        request = StringObj()
        request.value = uuid
        r: BooleanObj = self.stub.use_library(request)
        assert r.value == expected

    def test_switch_to_doc(self, relative_path: str, provider_type: str):
        request = LibGetReadyParamObj()
        request.relative_path = relative_path
        request.provider_type = provider_type
        res: StringObj = self.stub.make_library_ready(request)
        task_id: str = res.value
        assert bool(task_id)

        task_request = StringObj()
        task_request.value = task_id
        while True:
            p: TaskInfoObj = self.stub.get_task_state(task_request)
            TEST_LOGGER.info(
                f'Task in progress, state: {p.state}, phase_count: {p.phase_count}, phase_name: {p.phase_name}, progress: {p.progress}, error: {p.error}, duration: {p.duration}')
            res2: BooleanObj = self.stub.is_task_done(task_request)
            if res2.value:
                TEST_LOGGER.info(f'Task done, task ID: {task_id}')
                break
            time.sleep(1)

    def test_query_doc(self, text: str):
        request = DocLibQueryObj()
        request.text = text
        request.top_k = 10
        response: ListOfDocLibQueryResponseObj = self.stub.query_text(request)
        for i, res in enumerate(response.value):
            TEST_LOGGER.info(f'Query result {i + 1}: {res.text}')

    def test_make_image_library_ready(self):
        request = LibGetReadyParamObj()
        res: StringObj = self.stub.make_library_ready(request)
        task_id: str = res.value
        assert bool(task_id)

        task_request = StringObj()
        task_request.value = task_id
        while True:
            p: TaskInfoObj = self.stub.get_task_state(task_request)
            TEST_LOGGER.info(
                f'Task in progress, state: {p.state}, phase_count: {p.phase_count}, phase_name: {p.phase_name}, progress: {p.progress}, error: {p.error}, duration: {p.duration}')
            res2: BooleanObj = self.stub.is_task_done(task_request)
            if res2.value:
                TEST_LOGGER.info(f'Task done, task ID: {task_id}')
                break
            time.sleep(1)

    def test_image_for_image_search(self, sample_file_name: str):
        sample_image_path: str = f'{Path(__file__).parent.parent.parent.parent}/samples/{sample_file_name}'
        request = ImageLibQueryObj()
        request.image_data = open_image_as_base64(sample_image_path)  # type: ignore
        request.top_k = 10
        response: ListOfImageLibQueryResponseObj = self.stub.image_for_image_search(request)
        for i, res in enumerate(response.value):
            TEST_LOGGER.info(f'Query result {i + 1} relative_path: {res.path}, filename: {res.filename}')

    def test_text_for_image_search(self, text: str):
        request = ImageLibQueryObj()
        request.text = text
        request.top_k = 10
        response: ListOfImageLibQueryResponseObj = self.stub.text_for_image_search(request)
        for i, res in enumerate(response.value):
            TEST_LOGGER.info(f'Query result {i + 1} relative_path: {res.path}, filename: {res.filename}')

    def test_create_and_demolish_doc_lib(self):
        lib: LibInfo = doc_lib1
        self.test_create_library(lib)

        # Switch to library
        self.test_switch_to_library('1234', False)
        self.test_switch_to_library(lib.uuid, True)

        # Use a document
        self.test_switch_to_doc('/sample1.txt', 'DocProvider')

        # Do query
        self.test_query_doc('有意义的文字')
        self.test_query_doc('meaningful text')

        # Switch to another document
        self.test_switch_to_doc('/sample2.txt', 'DocProvider')

        # Do query
        self.test_query_doc('有意义的文字')
        self.test_query_doc('meaningful text')

        # Demolish library
        self.stub.demolish_library(VoidObj())

    def test_create_and_demolish_image_lib(self):
        lib: LibInfo = img_lib1
        self.test_create_library(lib)

        # Switch to library
        self.test_switch_to_library('1234', False)
        self.test_switch_to_library(lib.uuid, True)

        # Full scan
        self.test_make_image_library_ready()

        # Search image
        self.test_image_for_image_search('3.png')
        self.test_text_for_image_search('monkey')

        # Demolish library
        self.stub.demolish_library(VoidObj())

    def test_switch_library(self):
        self.test_create_library(doc_lib1)
        self.test_create_library(doc_lib2)

        self.test_switch_to_library(doc_lib1.uuid, True)
        self.test_switch_to_doc('/sample1.txt', 'DocProvider')

        self.test_switch_to_library(doc_lib2.uuid, True)
        self.test_switch_to_doc('/sample1.txt', 'DocProvider')

        self.test_switch_to_library(doc_lib1.uuid, True)
        self.stub.demolish_library(VoidObj())
        self.test_switch_to_library(doc_lib2.uuid, True)
        self.stub.demolish_library(VoidObj())
