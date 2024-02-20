T_VIDEO: set[str] = {'mp4', 'webm', 'avi', 'mov', 'flv', 'wmv', '3gp', '3g2', 'mkv', 'mpeg', 'mpg', 'm4v', 'h264', 'h265',
                     'hevc', 'rmvb', 'rm', 'asf', 'swf', 'vob', 'ts', 'm2ts', 'divx', 'f4v', 'm2v', 'ogv', 'mxf', 'mts', 'svi', 'smi', 'm2t'}
T_AUDIO: set[str] = {'mp3', "wav", "ogg", "mpeg", "aac", "3gpp", "3gpp2",
                     "aiff", "x-aiff", "amr", "mpga", 'oga', 'm4a', 'flac', 'aac', 'opus'}
T_IMAGE: set[str] = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
                     'svg', 'tiff', 'ico', 'jpe', 'jfif', 'pjpeg', 'pjp', 'avif', 'apng'}
T_CODE: set[str] = {'css', 'scss', 'html', 'py', 'js', 'cpp', 'c', 'java', 'go', 'php', 'ts', 'tsx', 'dart', 'sh', 'bat', 'h', 'hpp', 'rb', 'rs', 'cs',
                    'swift', 'kt', 'vb', 'lua', 'pl', 'm', 'r', 'sql', 'json', 'xml', 'yml', 'yaml', 'toml', 'ini', 'cfg', 'conf', 'md', 'markdown', 'rst', 'tex', 'latex'}
T_DOCUMENT: set[str] = {'docx', 'doc', 'csv', 'xls', 'xlsx', 'xlsm', 'xlsb', 'ods', 'ots', 'csv', 'tsv', 'ppt',
                        'pptx', 'odp', 'otp', 'odt', 'ott', 'rtf', 'epub', 'mobi', 'azw', 'azw3', 'fb2', 'djvu', 'xps', 'oxps', 'ps'}
T_ARCHIVE: set[str] = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'tz', 'cab', 'iso', 'xar', 'z'}

FILE_ICON_MAPPING: dict[str, set] = {
    'image.png': T_IMAGE,
    'audio.png': T_AUDIO,
    'video.png': T_VIDEO,
    'pdf.png': {'pdf'},
    'doc.png': T_DOCUMENT,
    'txt.png': {'txt'},
    'archive.png': T_ARCHIVE,
    'code.png': T_CODE,
}

FILE_CATEGORY_IMAGE = 'icon'
FILE_CATEGORY_VIDEO = 'video'
FILE_CATEGORY_AUDIO = 'audio'
FILE_CATEGORY_UNKNOWN = 'unknown'
