import grpc
from server.grpc.backend_pb2_grpc import GrpcServerStub
from server.grpc.obj_basic_pb2 import *
from server.grpc_server import GrpcServer
from tests.lib_info import *
from utils.lib_manager import LibraryManager
from utils.task_runner import TaskRunner

TEST_PORT: int = 50051

task_runner: TaskRunner = TaskRunner()
test_server: GrpcServer = GrpcServer(task_runner, LibraryManager(task_runner))


class GrpcClientForServerTest:
    def __init__(self, address: str = f'localhost:{TEST_PORT}'):
        self.stub: GrpcServerStub = GrpcServerStub(grpc.insecure_channel(address))

    def test_get_current_lib_info(self):
        response = self.stub.get_current_lib_info(VoidObj())
        print(response)

    def test_get_library_list(self):
        response = self.stub.get_library_list(VoidObj())
        print(response)
