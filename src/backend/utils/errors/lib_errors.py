class LibraryManagerException(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__(message)
        self.message: str | None = message
        self.code: int = code


class LibraryError(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__(message)
        self.message: str | None = message
        self.code: int = code


class DocProviderError(LibraryError):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__(message)
        self.message: str | None = message
        self.code: int = code


class LibraryErrorCode:
    pass
