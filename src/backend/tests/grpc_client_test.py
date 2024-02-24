import importlib
import time
from types import ModuleType

import grpc
from constants.env import GRPC_PORT
from loggers import logger as TEST_LOGGER
from server.grpc.backend_pb2_grpc import GrpcServerStub
from server.grpc.obj_basic_pb2 import *
from server.grpc.obj_shared_pb2 import *
from server.grpc_server import GrpcServer
from tests.lib_info import *
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

    def test_create_and_demolish_doc_lib(self):
        # Create library
        request = LibInfoObj()
        request.name = doc_lib1.name
        request.uuid = doc_lib1.uuid
        request.path = doc_lib1.path
        request.type = doc_lib1.type
        r1: BooleanObj = self.stub.create_library(request)
        assert r1.value, True

        # Switch to library
        request = StringObj()
        request.value = '1234'
        r2: BooleanObj = self.stub.use_library(request)
        assert r2.value == False
        request.value = doc_lib1.uuid
        r2: BooleanObj = self.stub.use_library(request)
        assert r2.value

        # Use a document
        request = LibGetReadyParamObj()
        request.relative_path = '/sample1.txt'
        request.provider_type = 'DocProvider'
        r3: StringObj = self.stub.make_library_ready(request)
        task_id: str = r3.value
        assert bool(task_id)

        task_request = StringObj()
        task_request.value = task_id
        while True:
            p: TaskInfoObj = self.stub.get_task_state(task_request)
            TEST_LOGGER.info(
                f'Task in progress, state: {p.state}, phase_count: {p.phase_count}, phase_name: {p.phase_name}, progress: {p.progress}, error: {p.error}, duration: {p.duration}')
            r: BooleanObj = self.stub.is_task_done(task_request)
            if r.value:
                TEST_LOGGER.info(f'Task done, task ID: {task_id}')
                break
            time.sleep(1)

        # Switch to another document
        request.relative_path = '/sample2.txt'

    def test_get_library_list(self):
        response = self.stub.get_library_list(VoidObj())
        print(response)
