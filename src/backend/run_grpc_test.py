import subprocess
from pathlib import Path

from tests.grpc_client_test import GrpcClientForServerTest


def run_test_server_in_background():
    server_file: str = f'{Path(__file__).parent}/run_grpc_server.py'
    subprocess.Popen(['/Users/chengjia/anaconda3/envs/llm_general/bin/python', server_file])


if __name__ == '__main__':
    run_test_server_in_background()

    test_client: GrpcClientForServerTest = GrpcClientForServerTest()
    test_client.test_get_current_lib_info()
    test_client.test_get_library_list()
