from constants.env import GRPC_PORT
from singletons import grpc_server

if __name__ == '__main__':
    grpc_server.start(GRPC_PORT)
