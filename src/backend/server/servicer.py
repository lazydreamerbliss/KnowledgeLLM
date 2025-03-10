import importlib
from datetime import datetime
from functools import wraps
from time import time
from types import ModuleType
from typing import Any

from library.document.doc_lib import DocumentLib
from library.document.doc_provider_base import DocumentType
from library.image.image_lib import ImageLib
from library.lib_base import LibraryBase
from loggers import rpc_logger as LOGGER
from server.grpc.backend_pb2_grpc import GrpcServerServicer
from server.grpc.obj_basic_pb2 import *
from server.grpc.obj_shared_pb2 import *
from utils.errors.lib_errors import LibraryManagerException
from utils.file_helper import open_base64_as_image
from utils.lib_manager import LibInfo, LibraryManager
from utils.task_runner import TaskInfo, TaskRunner

DOC_PROVIDER_MODULE_NAME: str = 'library.document.doc_provider'
WECHAT_PROVIDER_MODULE_NAME: str = 'library.document.wechat.wechat_history_provider'
DOC_PROVIDER_MODULE: ModuleType = importlib.import_module(DOC_PROVIDER_MODULE_NAME)
WECHAT_PROVIDER_MODULE: ModuleType = importlib.import_module(WECHAT_PROVIDER_MODULE_NAME)


def log_rpc_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        LOGGER.debug(f'RPC call started: {func.__name__}')
        start: float = time()
        try:
            result: Any = func(*args, **kwargs)
            time_taken: float = time() - start
            LOGGER.debug(f'RPC call finished: {func.__name__}, cost: {time_taken:.2f}s')
            return result
        except Exception as e:
            time_taken: float = time() - start
            LOGGER.error(f'RPC call failed: {func.__name__}, cost: {time_taken:.2f}s, error: {e}')
            raise e
    return wrapper


def get_doc_provider_type(type_name: str) -> type | None:
    if not type_name:
        return None

    potential_provider: type | None = None
    try:
        potential_provider = getattr(DOC_PROVIDER_MODULE, type_name)
    except AttributeError:
        pass
    if not potential_provider:
        try:
            potential_provider = getattr(WECHAT_PROVIDER_MODULE, type_name)
        except AttributeError:
            pass

    return potential_provider


class Servicer(GrpcServerServicer):
    def __init__(self, task_runner: TaskRunner, lib_manager: LibraryManager):
        self.__task_runner: TaskRunner = task_runner
        self.__lib_manager: LibraryManager = lib_manager

    def __process_lib_obj(self, request: LibInfoObj) -> LibInfo | None:
        name: str = request.name
        uuid: str = request.uuid
        path: str = request.path
        type: str = request.type
        if not name or not uuid or not path or not type:
            return None

        libInfo: LibInfo = LibInfo()
        libInfo.name = name
        libInfo.uuid = uuid
        libInfo.path = path
        libInfo.type = type
        return libInfo

    """
    Heat beat API
    """

    @log_rpc_call
    def heartbeat(self, request: VoidObj, context) -> BooleanObj:
        return BooleanObj(value=True)

    """`
    Task APIs
    """
    @log_rpc_call
    def get_task_state(self, request: StringObj, context) -> TaskInfoObj:
        response: TaskInfoObj = TaskInfoObj()
        task_id: str = request.value
        if not task_id:
            return response
        state: TaskInfo | None = self.__task_runner.get_task_state(task_id)
        if not state:
            return response

        response.id = state.id
        response.state = state.state
        response.phase_count = state.phase_count
        response.phase_name = state.phase_name  # type: ignore
        response.current_phase = state.current_phase
        response.progress = state.progress
        response.error = state.error  # type: ignore
        response.submitted_on.FromDatetime(state.submitted_on)  # Note: proto Timestamp cannot be directly assigned
        response.completed_on.FromDatetime(state.completed_on)  # Note: proto Timestamp cannot be directly assigned
        response.duration = state.duration
        return response

    @log_rpc_call
    def is_task_done(self, request: StringObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        if not request.value:
            return response

        response.value = self.__task_runner.is_task_done(request.value)
        return response

    @log_rpc_call
    def is_task_successful(self, request: StringObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        if not request.value:
            return response

        response.value = self.__task_runner.is_task_successful(request.value)
        return response

    @log_rpc_call
    def cancel_task(self, request: StringObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        if not request.value:
            return response

        response.value = self.__task_runner.cancel_task(request.value)
        return response

    """
    Library APIs for general purpose
    """
    @log_rpc_call
    def create_library(self, request: LibInfoObj, context) -> BooleanObj:
        libInfo: LibInfo | None = self.__process_lib_obj(request)
        if not libInfo:
            return BooleanObj(value=False)

        try:
            self.__lib_manager.create_library(libInfo, switch_to=False)
            return BooleanObj(value=True)
        except LibraryManagerException as e:
            LOGGER.error(f'Failed to create library: {e}')
            return BooleanObj(value=False)

    @log_rpc_call
    def use_library(self, request: StringObj, context) -> BooleanObj:
        if not request.value:
            return BooleanObj(value=False)
        return BooleanObj(value=self.__lib_manager.use_library(request.value))

    @log_rpc_call
    def demolish_library(self, request: VoidObj, context) -> BooleanObj:
        try:
            self.__lib_manager.demolish_library()
            return BooleanObj(value=True)
        except LibraryManagerException:
            LOGGER.error(f'Failed to demolish library')
            return BooleanObj(value=False)

    @log_rpc_call
    def get_current_lib_info(self, request: VoidObj, context) -> LibInfoObj:
        libInfo: LibInfo | None = self.__lib_manager.get_current_lib_info()
        if not libInfo:
            return LibInfoObj()

        response: LibInfoObj = LibInfoObj()
        response.name = libInfo.name
        response.uuid = libInfo.uuid
        response.path = libInfo.path
        response.type = libInfo.type
        return response

    @log_rpc_call
    def get_library_list(self, request: VoidObj, context) -> ListOfLibInfoObj:
        libList: list[LibInfo] = self.__lib_manager.get_library_list()
        response: ListOfLibInfoObj = ListOfLibInfoObj()
        for libInfo in libList:
            rpcLibInfo: LibInfoObj = LibInfoObj()
            rpcLibInfo.name = libInfo.name
            rpcLibInfo.uuid = libInfo.uuid
            rpcLibInfo.path = libInfo.path
            rpcLibInfo.type = libInfo.type
            response.value.append(rpcLibInfo)
        return response

    @log_rpc_call
    def get_library_path_list(self, request: VoidObj, context) -> ListOfStringObj:
        libPathList: list[str] = self.__lib_manager.get_library_path_list()
        response: ListOfStringObj = ListOfStringObj()
        response.value.extend(libPathList)
        return response

    @log_rpc_call
    def lib_exists(self, request: LibInfoObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        libInfo: LibInfo | None = self.__process_lib_obj(request)
        if not libInfo:
            return response
        response.value = self.__lib_manager.lib_exists(libInfo.uuid)
        return response

    @log_rpc_call
    def get_embedding_records(self, request: VoidObj, context) -> ListOfEmbeddingRecordObj:
        response: ListOfEmbeddingRecordObj = ListOfEmbeddingRecordObj()
        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance:
            return response

        records: dict[str, str] = instance.get_embedded_files()
        for k, v in records.items():
            record: EmbeddingRecordObj = EmbeddingRecordObj()
            record.relative_path = k
            record.uuid = v
            response.value.append(record)
        return response

    """
    Document library APIs
    """

    @log_rpc_call
    def make_document_ready(self, request: LibGetReadyParamObj, context) -> StringObj:
        potential_provider: type | None = get_doc_provider_type(request.provider_type)
        if not potential_provider:
            return StringObj(value=None, error=f'Invalid document provider type: {request.provider_type}')

        try:
            task_id: str | None = self.__lib_manager.make_library_ready(
                force_init=request.force_init,
                relative_path=request.relative_path,
                provider_type=potential_provider)
            if task_id is None:
                task_id = ''
            return StringObj(value=task_id)
        except LibraryManagerException as e:
            LOGGER.info(f'Failed to make document ready: {e}')
            return StringObj(value=None, error=str(e))

    @log_rpc_call
    def query_text(self, request: DocLibQueryObj, context) -> ListOfDocLibQueryResponseObj:
        response: ListOfDocLibQueryResponseObj = ListOfDocLibQueryResponseObj()
        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance or not isinstance(instance, DocumentLib) or not request.text:
            return response

        casted_instance: DocumentLib = instance
        doc_type: str = casted_instance.doc_type
        query_result: list[tuple] = casted_instance.query(request.text, request.top_k, request.rerank)
        for res in query_result:
            # Check if the data is from general document or chat history
            r: DocLibQueryResponseObj = DocLibQueryResponseObj()
            # Sample timestamp: 2024-02-24 13:20:03.123508
            timestamp_str: str = res[1]
            timestamp: datetime = datetime.fromisoformat(timestamp_str)
            r.timestamp.FromDatetime(timestamp)
            if doc_type == DocumentType.GENERAL.value:
                # (id, timestamp, text)
                r.text = res[2]
            elif doc_type == DocumentType.WECHAT_HISTORY.value:
                # (id, timestamp, sender, message, reply_to, replied_message)
                r.sender = res[2]
                r.message = res[3]
                r.reply_to = res[4]
                r.replied_message = res[5]
            response.value.append(r)

        return response

    """
    Image library APIs
    """

    @log_rpc_call
    def scan(self, request: LibGetReadyParamObj, context) -> StringObj:
        try:
            task_id: str | None = self.__lib_manager.make_library_ready(
                force_init=request.force_init,
                incremental=False)
            if task_id is None:
                task_id = ''
            return StringObj(value=task_id)
        except LibraryManagerException as e:
            LOGGER.info(f'Failed to scan image library: {e}')
            return StringObj(value=None, error=str(e))

    @log_rpc_call
    def incremental_scan(self, request: VoidObj, context) -> StringObj:
        try:
            task_id: str | None = self.__lib_manager.make_library_ready(incremental=True)
            if task_id is None:
                task_id = ''
            return StringObj(value=task_id)
        except LibraryManagerException as e:
            LOGGER.info(f'Failed to incrementally scan image library: {e}')
            return StringObj(value=None, error=str(e))

    @log_rpc_call
    def image_for_image_search(self, request: ImageLibQueryObj, context) -> ListOfImageLibQueryResponseObj:
        response: ListOfImageLibQueryResponseObj = ListOfImageLibQueryResponseObj()
        base64_data: str = request.image_data
        image, _ = open_base64_as_image(base64_data)
        if not image:
            LOGGER.error(f'Failed to read provided image data for image search')
            return response

        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance or not isinstance(instance, ImageLib):
            return response

        try:
            casted_instance: ImageLib = instance
            query_result: list[tuple] = casted_instance.image_for_image_search(image, request.top_k)
            for res in query_result:
                r: ImageLibQueryResponseObj = ImageLibQueryResponseObj()
                r.uuid = res[2]
                r.path = res[3]
                r.filename = res[4]
                response.value.append(r)
            return response
        except Exception as e:
            LOGGER.error(f'Image for image query failed, error: {e}')
            return response

    @log_rpc_call
    def text_for_image_search(self, request: ImageLibQueryObj, context) -> ListOfImageLibQueryResponseObj:
        response: ListOfImageLibQueryResponseObj = ListOfImageLibQueryResponseObj()
        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance or not isinstance(instance, ImageLib) or not request.text:
            return response

        try:
            casted_instance: ImageLib = instance
            query_result: list[tuple] = casted_instance.text_for_image_search(request.text, request.top_k)
            for res in query_result:
                r: ImageLibQueryResponseObj = ImageLibQueryResponseObj()
                r.uuid = res[2]
                r.path = res[3]
                r.filename = res[4]
                response.value.append(r)
            return response
        except Exception as e:
            LOGGER.error(f'Text for image query failed, error: {e}')
            return response

    @log_rpc_call
    def get_image_tags(self, request: ImageLibQueryObj, context) -> ListOfImageTagObj:
        # TODO: tagger is too slow, improve it firstly before adding tagger feature
        raise NotImplementedError('Not implemented yet')

    """
    File APIs
    """

    @log_rpc_call
    def move_files(self, request: FileMoveParamObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        relative_paths: list[str] = list(request.relative_paths)
        if not relative_paths or not request.dest_relative_path:
            return response

        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance:
            return response

        response.value = instance.move_files(relative_paths, request.dest_relative_path)
        return response

    @log_rpc_call
    def rename_file(self, request: FileRenameParamObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        if not request.relative_path or not request.new_name:
            return response

        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance:
            return response

        response.value = instance.rename_file(request.relative_path, request.new_name)
        return response

    @log_rpc_call
    def delete_files(self, request: ListOfStringObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        relative_paths: list[str] = list(request.value)
        if not relative_paths:
            return response

        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance:
            return response

        response.value = instance.delete_files(relative_paths)
        return response
