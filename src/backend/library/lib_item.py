class DirectoryItem:
    def __init__(self):
        self.name: str = ''  # The file/folder name
        self.parent_path: str = ''  # The path of parent folder, relative to the root of current library
        self.icon: str = ''
        self.dtc: str = ''
        self.dtm: str = ''


class FileItem(DirectoryItem):
    def __init__(self):
        self.size_b: int = -1  # The size of the file in bytes
        self.extension: str = ''  # The file extension
        self.supported: bool = False
        self.embedded: bool = False
