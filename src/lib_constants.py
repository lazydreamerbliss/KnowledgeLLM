sorted_by_labels: set[str] = {'Name', 'Date Created', 'Date Modified', 'Size'}
sorted_by_labels_ordered: list[str] = ['Name', 'Date Created', 'Date Modified', 'Size']
sorted_by_labels_CN: dict[str, str] = {
    'Name': '文件名',
    'Date Created': '创建时间',
    'Date Modified': '修改时间',
    'Size': '大小',
}
view_styles: list[str] = ['grid', 'list']
supported_formats: set[str] = {'mp4', "webm", "opgg", 'mp3', 'pdf', 'txt', 'html', 'css', 'svg', 'js', 'png', 'jpg'}


library_types: set[str] = {'image', 'video', 'document', 'general'}
library_types_CN: list[dict] = [
    {'name': 'image', 'cn_name': '图片库'},
    {'name': 'video', 'cn_name': '媒体库'},
    {'name': 'document', 'cn_name': '文档库'},
    {'name': 'general', 'cn_name': '综合仓库'},
]
