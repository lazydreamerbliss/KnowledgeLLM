class VectorDbError(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__()
        self.message: str | None = message
        self.code: int = code


class SqlTableError(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__()
        self.message: str | None = message
        self.code: int = code
