from tqdm import tqdm


class TqdmContext:
    def __init__(self,
                 begin: str,
                 end: str,
                 failure: str | None = None) -> None:
        self.begin: str = begin
        self.end: str = end
        self.failure: str | None = failure

    def __enter__(self) -> None:
        if self.begin:
            if self.end:
                tqdm.write(self.begin, end=' ')
            else:
                tqdm.write(self.begin)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # On exception, print the exception
        if exc_type is not None:
            if self.failure:
                tqdm.write(self.failure)
            else:
                tqdm.write(f'Exception: {exc_type}: {exc_val}')
        if self.end:
            tqdm.write(self.end)
