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


class LibTypes:
    """Define library types
    """
    IMAGE: str = 'image'
    VIDEO: str = 'video'
    DOCUMENT: str = 'document'
    GENERAL: str = 'general'


LIBRARY_TYPES: set[str] = {LibTypes.IMAGE, LibTypes.VIDEO, LibTypes.DOCUMENT, LibTypes.GENERAL}
LIBRARY_TYPES_CN: list[dict] = [
    {'name': LibTypes.IMAGE, 'cn_name': '图片库'},
    {'name': LibTypes.VIDEO, 'cn_name': '媒体库'},
    {'name': LibTypes.VIDEO, 'cn_name': '文档库'},
    {'name': LibTypes.GENERAL, 'cn_name': '综合仓库'},
]
