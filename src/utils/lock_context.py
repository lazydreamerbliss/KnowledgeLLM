from threading import Lock

from utils.exceptions.task_errors import LockAcquisitionFailure


class LockContext:
    def __init__(self, lock: Lock):
        self.acquired: bool = False
        self.__lock = lock

    def __enter__(self) -> 'LockContext':
        self.acquired = self.__lock.acquire(blocking=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            self.__lock.release()
