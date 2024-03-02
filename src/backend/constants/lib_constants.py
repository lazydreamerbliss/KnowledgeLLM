from utils.containable_enum import ContainableEnum

LIB_DATA_FOLDER: str = '.LibraryData'
INDEX_FOLDER: str = '.IndexStorage'  # All index files are stored in this folder under LIB_DATA_FOLDER
MEM_VDB_IDX_FILENAME: str = 'MemVectorDb.idx'  # Default mem-vector DB's index file name, if file name is not given


SORTED_BY_LABELS: set[str] = {'Name', 'Date Created', 'Date Modified', 'Size'}
SORTED_BY_LABELS_ORDERED: list[str] = ['Name', 'Date Created', 'Date Modified', 'Size']
SORTED_BY_LABELS_CN: dict[str, str] = {
    'Name': '文件名',
    'Date Created': '创建时间',
    'Date Modified': '修改时间',
    'Size': '大小',
}
VIEW_STYLES: list[str] = ['grid', 'list']


SUPPORTED_EXTENSIONS: set[str] = {'mp4', "webm", "opgg", 'mp3', 'pdf', 'txt', 'html', 'css', 'svg', 'js', 'png', 'jpg'}


class LibTypes(ContainableEnum):
    """Define library types
    """
    IMAGE = 'image'
    VIDEO = 'video'
    DOCUMENT = 'document'
    GENERAL = 'general'


LIBRARY_TYPES: set[str] = {
    LibTypes.IMAGE.value, LibTypes.VIDEO.value, LibTypes.DOCUMENT.value, LibTypes.GENERAL.value
}
LIBRARY_TYPES_CN: list[dict] = [
    {'name': LibTypes.IMAGE.value, 'cn_name': '图片库'},
    {'name': LibTypes.VIDEO.value, 'cn_name': '媒体库'},
    {'name': LibTypes.VIDEO.value, 'cn_name': '文档库'},
    {'name': LibTypes.GENERAL.value, 'cn_name': '综合仓库'},
]
