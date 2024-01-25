import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from threading import Lock
from typing import Callable


class TaskState:
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'
    FAULTED = 'FAULTED'
    CANCELLED = 'CANCELLED'


class TaskObj:
    """Define a task info under execution
    """

    def __init__(self, id: str, future: Future):
        self.id: str = id
        self.future: Future = future
        self.state: str = TaskState.IN_PROGRESS
        self.progress: int = 0  # TODO: make it reportable
        self.error: str | None = None
        self.submission_time: datetime = datetime.now()
        self.completion_time: datetime | None = None


class TaskCreationFailureException(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__()
        self.message: str | None = message
        self.code: int = code


class TaskRunner:
    def __init__(self, max_parallel_tasks: int = 5):
        self.tasks: dict[str, TaskObj] = dict()
        self.max_parallel_tasks: int = max_parallel_tasks
        self.thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_parallel_tasks)
        self.lock = Lock()

    def __run_task(self, task_id: str, task_func: Callable, args: tuple, kwargs: dict):
        """Run given task
        """
        try:
            task_func(*args, **kwargs)
            self.tasks[task_id].state = TaskState.FINISHED
            self.tasks[task_id].completion_time = datetime.now()
            self.tasks[task_id].progress = 100
        except Exception as e:
            self.tasks[task_id].state = TaskState.FAULTED
            self.tasks[task_id].completion_time = datetime.now()
            self.tasks[task_id].error = str(e)

    def __get_active_task_count(self) -> int:
        with self.lock:
            res: int = 0
            for id in self.tasks:
                if self.tasks[id].state == TaskState.IN_PROGRESS:
                    res += 1
            return res

    def submit_task(self, task_func: Callable, callback_lambda: Callable | None, *args, **kwargs):
        """Submit a function as a concurrent task and executing in the background
        """
        if self.__get_active_task_count() >= self.max_parallel_tasks:
            raise TaskCreationFailureException('Maximum number of parallel tasks exceeded')

        with self.lock:
            task_id: str = str(uuid.uuid4())
            future: Future = self.thread_pool.submit(self.__run_task, task_id, task_func, args, kwargs)
            self.tasks[task_id] = TaskObj(task_id, future)

        if callback_lambda:
            future.add_done_callback(callback_lambda)
        return task_id

    def cancel_task(self, task_id: str):
        """Cancel an executing task
        """
        if task_id in self.tasks:
            future = self.tasks[task_id].future
            if not future.done():
                future.cancel()
                self.tasks[task_id].state = TaskState.CANCELLED
                self.tasks[task_id].completion_time = datetime.now()

    def check_task_state(self, task_id: str) -> TaskObj | None:
        """Check the running state of a submitted task
        """
        return self.tasks.get(task_id, None)
