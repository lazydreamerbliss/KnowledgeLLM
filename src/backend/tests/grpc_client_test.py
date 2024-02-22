import grpc
from constants.env import GRPC_PORT
from server.grpc.backend_pb2_grpc import GrpcServerStub
from server.grpc.obj_basic_pb2 import *
from server.grpc.obj_shared_pb2 import *
from server.grpc_server import GrpcServer
from tests.lib_info import *
from utils.lib_manager import LibraryManager
from utils.task_runner import TaskRunner

task_runner: TaskRunner = TaskRunner()
test_server: GrpcServer = GrpcServer(task_runner, LibraryManager(task_runner))


class GrpcClientForServerTest:
    def __init__(self, address: str = f'localhost:{GRPC_PORT}'):
        self.stub: GrpcServerStub = GrpcServerStub(grpc.insecure_channel(address))

    def test_heartbeat(self):
        response = self.stub.heartbeat(VoidObj())
        print(response)

    def test_create_and_demolish_doc_lib(self):
        request: LibInfoObj = LibInfoObj()
        request.name = doc_lib1.name
        request.uuid = doc_lib1.uuid
        request.path = doc_lib1.path
        request.type = doc_lib1.type

        r1: BooleanObj = self.stub.create_library(request)
        assert r1.value, True

    def test_get_library_list(self):
        response = self.stub.get_library_list(VoidObj())
        print(response)
