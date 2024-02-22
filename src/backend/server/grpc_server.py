from concurrent import futures

import grpc
from server.grpc.backend_pb2_grpc import add_GrpcServerServicer_to_server
from server.servicer import Servicer
from utils.lib_manager import LibraryManager
from utils.task_runner import TaskRunner


class GrpcServer(Servicer):
    def __init__(self, task_runner: TaskRunner, lib_manager: LibraryManager):
        self.__server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_GrpcServerServicer_to_server(Servicer(task_runner, lib_manager), self.__server)

    def start(self, port: int):
        self.__server.add_insecure_port(f"[::]:{port}")
        self.__server.start()
        self.__server.wait_for_termination()
