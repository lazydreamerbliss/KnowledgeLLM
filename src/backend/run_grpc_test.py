import subprocess
import time
from pathlib import Path

from constants.env import IS_LINUX, IS_OSX
from tests.grpc_client_test import GrpcClientForServerTest


class TestServer:
    def __init__(self) -> None:
        server_file: str = f'{Path(__file__).parent}/run_grpc_server.py'
        if IS_OSX:
            self.process = subprocess.Popen(
                ['nohup', '/Users/chengjia/anaconda3/envs/llm_general/bin/python', server_file])
        elif IS_LINUX:
            self.process = subprocess.Popen(
                ['nohup', '/home/chengjia/anaconda3/envs/llm_general/bin/python', server_file])
        self.pid: int = self.process.pid

        print(f'gRPC server started with pid: {self.pid}')
        # Sleep for some time to let the server start, otherwise "Failed to
        # connect to remote host: Connection refuse" might occur
        time.sleep(3)
        self.pid: int = self.process.pid

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Kill the server on test completion, wait for some time to allow possible pending requests to complete
        time.sleep(10)
        subprocess.Popen(['kill', str(self.pid)])
        print(f'gRPC server killed successfully with pid: {self.pid}')


def run_test_client():
    test_client: GrpcClientForServerTest = GrpcClientForServerTest()
    test_client.test_heartbeat()
    # test_client.test_create_and_demolish_doc_lib()
    # test_client.test_create_and_demolish_image_lib()
    ##test_client.test_file_moving()
    #test_client.test_file_rename()
    test_client.test_complex_moving()


def run_test_client_wrapper(run_server: bool = False):
    if run_server:
        with TestServer():
            run_test_client()
    else:
        run_test_client()


if __name__ == '__main__':
    run_test_client_wrapper(run_server=False)
