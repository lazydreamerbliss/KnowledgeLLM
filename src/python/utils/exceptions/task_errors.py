class TaskCreationFailureException(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__(message)
        self.message: str | None = message
        self.code: int = code


class TaskCancelFailureException(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__(message)
        self.message: str | None = message
        self.code: int = code


class TaskCancellationException(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__(message)
        self.message: str | None = message
        self.code: int = code


class LockAcquisitionFailure(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__(message)
        self.message: str | None = message
        self.code: int = code
