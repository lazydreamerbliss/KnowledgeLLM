import subprocess
import time
from pathlib import Path

from tests.grpc_client_test import GrpcClientForServerTest


def run_test_server_in_new_process() -> int:
    server_file: str = f'{Path(__file__).parent}/run_grpc_server.py'
    # process = subprocess.Popen(['/Users/chengjia/anaconda3/envs/llm_general/bin/python', server_file])
    process = subprocess.Popen(['nohup', '/home/chengjia/anaconda3/envs/llm_general/bin/python', server_file])
    return process.pid


if __name__ == '__main__':
    pid: int = run_test_server_in_new_process()
    print(f'gRPC server started with pid: {pid}')

    # Sleep for some time to let the server start, otherwise "Failed to
    # connect to remote host: Connection refuse" might occur
    time.sleep(3)

    test_client: GrpcClientForServerTest = GrpcClientForServerTest()
    test_client.test_get_current_lib_info()
    test_client.test_get_library_list()

    # Kill the server on test completion, wait for some time to allow possible pending requests to complete
    time.sleep(2)
    subprocess.Popen(['kill', str(pid)])
    print(f'killed gRPC server with pid: {pid}')
