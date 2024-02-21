from library.document.doc_lib import DocumentLib
from library.document.doc_provider_base import DocumentType
from library.image.image_lib import ImageLib
from library.lib_base import LibraryBase
from PIL import Image
from server.grpc.backend_pb2_grpc import GrpcServerServicer
from server.grpc.obj_basic_pb2 import *
from server.grpc.obj_shared_pb2 import *
from utils.exceptions.lib_errors import LibraryManagerException
from utils.lib_manager import LibInfo, LibraryManager
from utils.task_runner import TaskInfo, TaskRunner


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
    Task APIs
    """

    def get_task_state(self, request: StringObj, context) -> TaskInfoObj:
        response: TaskInfoObj = TaskInfoObj()
        if not request.value:
            return response
        state: TaskInfo | None = self.__task_runner.get_task_state(request.value)
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

    def create_library(self, request: LibInfoObj, context) -> BooleanObj:
        libInfo: LibInfo | None = self.__process_lib_obj(request)
        if not libInfo:
            return BooleanObj(value=False)

        try:
            self.__lib_manager.create_library(libInfo, switch_to=False)
            return BooleanObj(value=True)
        except LibraryManagerException:
            return BooleanObj(value=False)

    def use_library(self, request: LibInfoObj, context) -> BooleanObj:
        targetLibInfo: LibInfo | None = self.__process_lib_obj(request)
        if not targetLibInfo:
            return BooleanObj(value=False)

        return BooleanObj(value=self.__lib_manager.use_library(targetLibInfo.uuid))

    def demolish_library(self, request: VoidObj, context) -> BooleanObj:
        try:
            self.__lib_manager.demolish_library()
            return BooleanObj(value=True)
        except LibraryManagerException:
            return BooleanObj(value=False)

    def make_library_ready(self, request: LibGetReadyParamObj, context) -> StringObj:
        try:
            potential_provider: type | None = globals().get(request.provider_type, None)
            task_id: str = self.__lib_manager.make_library_ready(
                force_init=request.force_init,
                relative_path=request.relative_path,
                provider_type=potential_provider)
            return StringObj(value=task_id)
        except LibraryManagerException:
            return StringObj(value='')

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

    def get_library_path_list(self, request: VoidObj, context) -> ListOfStringObj:
        libPathList: list[str] = self.__lib_manager.get_library_path_list()
        response: ListOfStringObj = ListOfStringObj()
        response.value.extend(libPathList)
        return response

    def lib_exists(self, request: LibInfoObj, context) -> BooleanObj:
        libInfo: LibInfo | None = self.__process_lib_obj(request)
        if not libInfo:
            return BooleanObj(value=False)

        return BooleanObj(value=self.__lib_manager.lib_exists(libInfo.uuid))

    """
    Document library APIs
    """

    def query(self, request: DocLibQueryObj, context) -> ListOfDocLibQueryResponseObj:
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
            if doc_type == DocumentType.GENERAL:
                # The text column ['text', 'TEXT'] is the 3rd column of document table, so row[2] is the key info
                r.text = res[2]
            elif doc_type == DocumentType.WECHAT_HISTORY:
                # The message & replied message column ['message', 'TEXT'] and ['replied_message', 'TEXT'] are 4th and 6th columns of chat history table
                r.sender = res[2]
                r.message = res[3]
                r.reply_to = res[4]
                r.replied_message = res[5]
            response.value.append(r)

        return response

    """
    Document library APIs
    """

    def image_for_image_search(self, request: ImageLibQueryObj, context) -> ListOfImageLibQueryResponseObj:
        response: ListOfImageLibQueryResponseObj = ListOfImageLibQueryResponseObj()
        image_data: bytes = request.image_data
        if not image_data:
            return response

        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance or not isinstance(instance, ImageLib):
            return response

        try:
            image: Image.Image = Image.open(image_data)
            casted_instance: ImageLib = instance
            query_result: list[tuple] = casted_instance.image_for_image_search(image, request.top_k)
            for res in query_result:
                r: ImageLibQueryResponseObj = ImageLibQueryResponseObj()
                r.uuid = res[2]
                r.path = res[3]
                r.filename = res[4]
                response.value.append(r)
            return response
        except Exception:
            return response

    def text_for_image_search(self, request: ImageLibQueryObj, context) -> ListOfImageLibQueryResponseObj:
        response: ListOfImageLibQueryResponseObj = ListOfImageLibQueryResponseObj()
        instance: LibraryBase | None = self.__lib_manager.instance
        if not instance or not isinstance(instance, ImageLib) or not request.text:
            return response

        casted_instance: ImageLib = instance
        query_result: list[tuple] = casted_instance.text_for_image_search(request.text, request.top_k)
        for res in query_result:
            r: ImageLibQueryResponseObj = ImageLibQueryResponseObj()
            r.uuid = res[2]
            r.path = res[3]
            r.filename = res[4]
            response.value.append(r)
        return response

    def get_image_tags(self, request: ImageLibQueryObj, context) -> ListOfImageTagObj:
        # TODO
        raise NotImplementedError('Not implemented yet')
