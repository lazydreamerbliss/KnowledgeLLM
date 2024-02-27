from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LibInfoObj(_message.Message):
    __slots__ = ("name", "uuid", "path", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    uuid: str
    path: str
    type: str
    def __init__(self, name: _Optional[str] = ..., uuid: _Optional[str] = ..., path: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class ListOfLibInfoObj(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[LibInfoObj]
    def __init__(self, value: _Optional[_Iterable[_Union[LibInfoObj, _Mapping]]] = ...) -> None: ...

class LibGetReadyParamObj(_message.Message):
    __slots__ = ("force_init", "relative_path", "provider_type")
    FORCE_INIT_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    force_init: bool
    relative_path: str
    provider_type: str
    def __init__(self, force_init: bool = ..., relative_path: _Optional[str] = ..., provider_type: _Optional[str] = ...) -> None: ...

class TaskInfoObj(_message.Message):
    __slots__ = ("id", "state", "phase_count", "phase_name", "current_phase", "progress", "error", "submitted_on", "completed_on", "duration")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PHASE_COUNT_FIELD_NUMBER: _ClassVar[int]
    PHASE_NAME_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PHASE_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_ON_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: str
    phase_count: int
    phase_name: str
    current_phase: int
    progress: int
    error: str
    submitted_on: _timestamp_pb2.Timestamp
    completed_on: _timestamp_pb2.Timestamp
    duration: int
    def __init__(self, id: _Optional[str] = ..., state: _Optional[str] = ..., phase_count: _Optional[int] = ..., phase_name: _Optional[str] = ..., current_phase: _Optional[int] = ..., progress: _Optional[int] = ..., error: _Optional[str] = ..., submitted_on: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed_on: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[int] = ...) -> None: ...

class DocLibQueryObj(_message.Message):
    __slots__ = ("text", "top_k", "rerank")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    RERANK_FIELD_NUMBER: _ClassVar[int]
    text: str
    top_k: int
    rerank: bool
    def __init__(self, text: _Optional[str] = ..., top_k: _Optional[int] = ..., rerank: bool = ...) -> None: ...

class DocLibQueryResponseObj(_message.Message):
    __slots__ = ("timestamp", "text", "sender", "message", "reply_to", "replied_message")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    REPLY_TO_FIELD_NUMBER: _ClassVar[int]
    REPLIED_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    text: str
    sender: str
    message: str
    reply_to: str
    replied_message: str
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., text: _Optional[str] = ..., sender: _Optional[str] = ..., message: _Optional[str] = ..., reply_to: _Optional[str] = ..., replied_message: _Optional[str] = ...) -> None: ...

class ListOfDocLibQueryResponseObj(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[DocLibQueryResponseObj]
    def __init__(self, value: _Optional[_Iterable[_Union[DocLibQueryResponseObj, _Mapping]]] = ...) -> None: ...

class ImageLibQueryObj(_message.Message):
    __slots__ = ("image_data", "top_k", "text")
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    image_data: str
    top_k: int
    text: str
    def __init__(self, image_data: _Optional[str] = ..., top_k: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class ImageLibQueryResponseObj(_message.Message):
    __slots__ = ("uuid", "path", "filename")
    UUID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    path: str
    filename: str
    def __init__(self, uuid: _Optional[str] = ..., path: _Optional[str] = ..., filename: _Optional[str] = ...) -> None: ...

class ListOfImageLibQueryResponseObj(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[ImageLibQueryResponseObj]
    def __init__(self, value: _Optional[_Iterable[_Union[ImageLibQueryResponseObj, _Mapping]]] = ...) -> None: ...

class ImageTagObj(_message.Message):
    __slots__ = ("tag", "confidence")
    TAG_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    tag: str
    confidence: float
    def __init__(self, tag: _Optional[str] = ..., confidence: _Optional[float] = ...) -> None: ...

class ListOfImageTagObj(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[ImageTagObj]
    def __init__(self, value: _Optional[_Iterable[_Union[ImageTagObj, _Mapping]]] = ...) -> None: ...

class FileMoveParamObj(_message.Message):
    __slots__ = ("relative_path", "dest_relative_path")
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    DEST_RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    relative_path: str
    dest_relative_path: str
    def __init__(self, relative_path: _Optional[str] = ..., dest_relative_path: _Optional[str] = ...) -> None: ...

class FileRenameParamObj(_message.Message):
    __slots__ = ("relative_path", "new_name")
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    NEW_NAME_FIELD_NUMBER: _ClassVar[int]
    relative_path: str
    new_name: str
    def __init__(self, relative_path: _Optional[str] = ..., new_name: _Optional[str] = ...) -> None: ...

class FileDeleteParamObj(_message.Message):
    __slots__ = ("relative_path", "provider_type")
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    relative_path: str
    provider_type: str
    def __init__(self, relative_path: _Optional[str] = ..., provider_type: _Optional[str] = ...) -> None: ...
