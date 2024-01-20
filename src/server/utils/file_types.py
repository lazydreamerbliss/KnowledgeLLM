video_types: set[str] = {'mp4', 'webm', 'avi', 'mov', 'flv', 'wmv', '3gp', '3g2', 'mkv', 'mpeg', 'mpg', 'm4v', 'h264', 'h265',
                         'hevc', 'rmvb', 'rm', 'asf', 'swf', 'vob', 'ts', 'm2ts', 'divx', 'f4v', 'm2v', 'ogv', 'mxf', 'mts', 'svi', 'smi', 'm2t'}
audio_types: set[str] = {'mp3', "wav", "ogg", "mpeg", "aac", "3gpp", "3gpp2",
                         "aiff", "x-aiff", "amr", "mpga", 'oga', 'm4a', 'flac', 'aac', 'opus'}
image_types: set[str] = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
                         'svg', 'tiff', 'ico', 'jpe', 'jfif', 'pjpeg', 'pjp', 'avif', 'apng'}
code_types: set[str] = {'css', 'scss', 'html', 'py', 'js', 'cpp', 'c', 'java', 'go', 'php', 'ts', 'tsx', 'dart', 'sh', 'bat', 'h', 'hpp', 'rb', 'rs', 'cs',
                        'swift', 'kt', 'vb', 'lua', 'pl', 'm', 'r', 'sql', 'json', 'xml', 'yml', 'yaml', 'toml', 'ini', 'cfg', 'conf', 'md', 'markdown', 'rst', 'tex', 'latex', 'svg'}


ICON_MAPPING: dict[str, set] = {
    'image.png': image_types,
    'audio.png': audio_types,
    'video.png': video_types,
    'pdf.png': {'pdf'},
    'doc.png': {'docx', 'doc'},
    'txt.png': {'txt'},
    'archive.png': {'zip', 'rar', '7z'},
    'code.png': code_types,
}
