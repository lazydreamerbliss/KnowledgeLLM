from PIL import Image

from python.lib_manager import LibInfoObj, LibraryManager
from python.library.document.doc_lib import DocumentLib
from python.library.image.image_lib import ImageLib
from python.library.lib_base import LibraryBase
from python.server.grpc_server_pb2 import *
from python.server.grpc_server_pb2_grpc import GrpcServerServicer
from python.utils.exceptions.lib_errors import LibraryManagerException
from python.utils.task_runner import TaskObj, TaskRunner


class Servicer(GrpcServerServicer):
    def __init__(self, task_runner: TaskRunner, lib_manager: LibraryManager):
        self.__task_runner: TaskRunner = task_runner
        self.__lib_manager: LibraryManager = lib_manager

    def __process_lib_obj(self, request: RpcLibInfoObj) -> LibInfoObj | None:
        name: str = request.name
        uuid: str = request.uuid
        path: str = request.path
        type: str = request.type
        if not name or not uuid or not path or not type:
            return None

        libInfo: LibInfoObj = LibInfoObj()
        libInfo.name = name
        libInfo.uuid = uuid
        libInfo.path = path
        libInfo.type = type
        return libInfo

    """
    Task APIs
    """

    def get_task_state(self, request: StringObj, context) -> RpcTaskObj:
        response: RpcTaskObj = RpcTaskObj()
        if not request.value:
            return response
        state: TaskObj | None = self.__task_runner.get_task_state(request.value)
        if not state:
            return response

        response.id = state.id
        response.state = state.state
        response.phase_count = state.phase_count
        response.phase_name = state.phase_name  # type: ignore
        response.current_phase = state.current_phase
        response.progress = state.progress
        response.error = state.error  # type: ignore
        response.submitted_on = state.submitted_on  # type: ignore
        response.completed_on = state.completed_on  # type: ignore
        response.duration = state.duration
        return response

    def is_task_done(self, request: StringObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        if not request.value:
            return response

        response.value = self.__task_runner.is_task_done(request.value)
        return response

    def is_task_successful(self, request: StringObj, context) -> BooleanObj:
        response: BooleanObj = BooleanObj()
        response.value = False
        if not request.value:
            return response

        response.value = self.__task_runner.is_task_successful(request.value)
        return response

    """
    Library APIs for general purpose
    """

    def create_library(self, request: RpcLibInfoObj, context) -> BooleanObj:
        libInfo: LibInfoObj | None = self.__process_lib_obj(request)
        if not libInfo:
            return BooleanObj(value=False)

        try:
            self.__lib_manager.create_library(libInfo, switch_to=False)
            return BooleanObj(value=True)
        except LibraryManagerException:
            return BooleanObj(value=False)

    def use_library(self, request: RpcLibInfoObj, context) -> BooleanObj:
        targetLibInfo: LibInfoObj | None = self.__process_lib_obj(request)
        if not targetLibInfo:
            return BooleanObj(value=False)

        return BooleanObj(value=self.__lib_manager.use_library(targetLibInfo.uuid))

    def demolish_library(self, request: VoidObj, context) -> BooleanObj:
        try:
            self.__lib_manager.demolish_library()
            return BooleanObj(value=True)
        except LibraryManagerException:
            return BooleanObj(value=False)

    def make_library_ready(self, request: LibGetReadyParams, context) -> StringObj:
        try:
            potential_provider: type | None = globals().get(request.provider_type, None)
            task_id: str = self.__lib_manager.make_library_ready(
                force_init=request.force_init,
                relative_path=request.relative_path,
                provider_type=potential_provider)
            return StringObj(value=task_id)
        except LibraryManagerException:
            return StringObj(value='')

    def get_current_lib_info(self, request: VoidObj, context) -> RpcLibInfoObj:
        libInfo: LibInfoObj | None = self.__lib_manager.get_current_lib_info()
        if not libInfo:
            return RpcLibInfoObj()

        response: RpcLibInfoObj = RpcLibInfoObj()
        response.name = libInfo.name
        response.uuid = libInfo.uuid
        response.path = libInfo.path
        response.type = libInfo.type
        return response

    def get_library_list(self, request: VoidObj, context) -> ListOfRpcLibInfoObj:
        libList: list[LibInfoObj] = self.__lib_manager.get_library_list()
        response: ListOfRpcLibInfoObj = ListOfRpcLibInfoObj()
        for libInfo in libList:
            rpcLibInfo: RpcLibInfoObj = RpcLibInfoObj()
            rpcLibInfo.name = libInfo.name
            rpcLibInfo.uuid = libInfo.uuid
            rpcLibInfo.path = libInfo.path
            rpcLibInfo.type = libInfo.type
            response.value.append(rpcLibInfo)
        return response

    def get_library_path_list(self, request: VoidObj, context) -> ListOfStrings:
        libPathList: list[str] = self.__lib_manager.get_library_path_list()
        response: ListOfStrings = ListOfStrings()
        response.value.extend(libPathList)
        return response

    def lib_exists(self, request: RpcLibInfoObj, context) -> BooleanObj:
        libInfo: LibInfoObj | None = self.__process_lib_obj(request)
        if not libInfo:
            return BooleanObj(value=False)

        return BooleanObj(value=self.__lib_manager.lib_exists(libInfo.uuid))

    """
    Document library APIs
    """

    def query(self, request: DocLibQueryObj, context) -> ListOfStrings:
        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance or not isinstance(instance, DocumentLib) or not request.text:
            return ListOfStrings()

        casted_instance: DocumentLib = instance
        res: list[tuple] = casted_instance.query(request.text, request.top_k, request.rerank)

    """
    Document library APIs
    """

    def image_for_image_search(self, request: ImageLibQueryObj, context) -> ListOfStrings:
        image_data: bytes = request.image_data
        if not image_data:
            return ListOfStrings()

        try:
            image: Image.Image = Image.open(image_data)
            instance: LibraryBase | None = self.__lib_manager.instance
            if not instance:
                return ListOfStrings()

            casted_instance: ImageLib = instance
            res: list[tuple] = casted_instance.image_for_image_search(image, request.top_k)
            
            
        except Exception:
            return ListOfStrings()

    def text_for_image_search(self, request: ImageLibQueryObj, context) -> ListOfStrings:
        pass

    def get_image_tags(self, request: ImageLibQueryObj, context) -> ListOfStrings:
        pass
