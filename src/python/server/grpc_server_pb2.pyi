from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VoidObj(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RpcLibInfoObj(_message.Message):
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

class ListOfRpcLibInfoObj(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[RpcLibInfoObj]
    def __init__(self, value: _Optional[_Iterable[_Union[RpcLibInfoObj, _Mapping]]] = ...) -> None: ...

class LibGetReadyParams(_message.Message):
    __slots__ = ("relative_path", "force_init", "provider_type")
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    FORCE_INIT_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    relative_path: str
    force_init: bool
    provider_type: str
    def __init__(self, relative_path: _Optional[str] = ..., force_init: bool = ..., provider_type: _Optional[str] = ...) -> None: ...

class RpcTaskObj(_message.Message):
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

class ImageLibQueryObj(_message.Message):
    __slots__ = ("image_data", "top_k", "text")
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    image_data: bytes
    top_k: int
    text: str
    def __init__(self, image_data: _Optional[bytes] = ..., top_k: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class BooleanObj(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: bool = ...) -> None: ...

class StringObj(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class ListOfStrings(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, value: _Optional[_Iterable[str]] = ...) -> None: ...
