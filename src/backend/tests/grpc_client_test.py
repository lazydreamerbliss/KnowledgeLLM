import time

import grpc
from constants.env import GRPC_PORT
from loggers import test_logger as TEST_LOGGER
from server.grpc.backend_pb2_grpc import GrpcServerStub
from server.grpc.obj_basic_pb2 import *
from server.grpc.obj_shared_pb2 import *
from server.grpc_server import GrpcServer
from tests.lib_info import *
from utils.file_helper import open_image_as_base64
from utils.lib_manager import UUID_EMPTY, LibraryManager
from utils.task_runner import TaskRunner

task_runner: TaskRunner = TaskRunner()
test_server: GrpcServer = GrpcServer(task_runner, LibraryManager(task_runner))


class GrpcClientForServerTest:
    def __init__(self, address: str = f'localhost:{GRPC_PORT}'):
        self.stub: GrpcServerStub = GrpcServerStub(grpc.insecure_channel(address))

    def get_embedding_records(self):
        request = VoidObj()
        response: ListOfEmbeddingRecordObj = self.stub.get_embedding_records(request)
        for record in response.value:
            TEST_LOGGER.info(f'Embedding record: {record.relative_path} - {record.uuid}')

    def test_heartbeat(self):
        response: BooleanObj = self.stub.heartbeat(VoidObj())
        TEST_LOGGER.info(f'Heartbeat response: {response.value}')

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
        res: StringObj = self.stub.make_document_ready(request)
        task_id: str = res.value
        assert bool(task_id)

        if task_id == UUID_EMPTY:
            return

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

    def test_scan(self):
        request = LibGetReadyParamObj()
        request.force_init = True
        res: StringObj = self.stub.scan(request)
        task_id: str = res.value
        assert bool(task_id)

        if task_id == UUID_EMPTY:
            return

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

    def test_move_file(self, src_files_relatives: list[str], dst_folder_relative: str):
        request = FileMoveParamObj()
        request.relative_paths.extend(src_files_relatives)
        request.dest_relative_path = dst_folder_relative
        res: BooleanObj = self.stub.move_files(request)
        TEST_LOGGER.info(f'Move files response: {res.value}')

    def test_rename_file(self, src_file_relative: str, new_name: str):
        request = FileRenameParamObj()
        request.relative_path = src_file_relative
        request.new_name = new_name
        res: BooleanObj = self.stub.rename_file(request)
        TEST_LOGGER.info(f'Rename file response: {res.value}')

    def test_delete_files(self, src_files_relatives: list[str]):
        request = ListOfStringObj()
        request.value.extend(src_files_relatives)
        res: BooleanObj = self.stub.delete_files(request)
        TEST_LOGGER.info(f'Delete files response: {res.value}')

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
        self.test_scan()

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

    def test_file_moving(self):
        lib: LibInfo = img_lib1
        self.test_create_library(lib)

        # Switch to library
        self.test_switch_to_library(lib.uuid, True)

        # Full scan to create file records
        self.test_scan()

        # Move files
        files = ['/sample1.jpg', '/sample2.jpg', '/sample3.jpg', '/sample4.jpg']
        self.test_move_file(files, '/F1')
        self.get_embedding_records()
        files = ['/F1/sample1.jpg', '/F1/sample2.jpg', '/F1/sample3.jpg', '/F1/sample4.jpg']
        self.test_move_file(files, '/')
        self.get_embedding_records()
        files = ['/sample1.jpg', '/sample2.jpg', '/sample3.jpg', '/sample4.jpg']
        self.test_move_file(files, '/F1/F2/F3')
        self.get_embedding_records()
        files = ['/F1/F2/F3/sample1.jpg', '/F1/F2/F3/sample2.jpg', '/F1/F2/F3/sample3.jpg', '/F1/F2/F3/sample4.jpg']
        self.test_move_file(files, '/')
        self.get_embedding_records()

    def test_file_rename(self):
        lib: LibInfo = img_lib1
        self.test_create_library(lib)

        # Switch to library
        self.test_switch_to_library(lib.uuid, True)

        # Full scan to create file records
        self.test_scan()

        # Rename files
        self.test_rename_file('/sample1.jpg', 'new_sample1.jpg')
        self.test_rename_file('/sample2.jpg', 'new_sample2.jpg')
        self.test_rename_file('/sample3.jpg', 'new_sample3.jpg')
        self.test_rename_file('/sample4.jpg', 'new_sample4.jpg')
        self.get_embedding_records()
        self.test_rename_file('/new_sample1.jpg', 'sample1.jpg')
        self.test_rename_file('/new_sample2.jpg', 'sample2.jpg')
        self.test_rename_file('/new_sample3.jpg', 'sample3.jpg')
        self.test_rename_file('/new_sample4.jpg', 'sample4.jpg')
        self.get_embedding_records()

    def test_complex_moving(self):
        lib: LibInfo = img_lib1
        self.test_create_library(lib)

        # Switch to library
        self.test_switch_to_library(lib.uuid, True)

        # Full scan to create file records
        self.test_scan()

        # Move files to /F1 to prepare for the following tests
        files = ['/sample1.jpg', '/sample2.jpg', '/sample3.jpg', '/sample4.jpg']
        self.test_move_file(files, '/F1')
        self.get_embedding_records()

        # Move folder: /F1 -> /K1/K2/K3/F1
        files = ['/F1']
        self.test_move_file(files, '/K1/K2/K3')
        self.get_embedding_records()
        files = ['/K1/K2/K3/F1']
        self.test_move_file(files, '/')
        self.get_embedding_records()
        self.test_rename_file('/F1', 'F2')
        self.get_embedding_records()
        files = ['/F2']
        self.test_move_file(files, '/AAA/BBB')
        self.get_embedding_records()
        self.test_delete_files(['/AAA/BBB/F2'])
        self.get_embedding_records()
