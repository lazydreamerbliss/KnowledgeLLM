import uuid
from threading import Lock, RLock

from utils.exceptions.task_errors import LockAcquisitionFailure


class LockContext:
    def __init__(self, lock: Lock | RLock):
        self.acquired: bool = False
        self.__lock = lock

    def __enter__(self) -> 'LockContext':
        self.acquired = self.__lock.acquire(blocking=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            self.__lock.release()
