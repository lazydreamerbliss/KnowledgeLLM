import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from threading import Lock
from typing import Callable

EXPIRATION_DURATION = 86400  # Automatically cleanup finished tasks after these seconds


class TaskState:
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'
    FAULTED = 'FAULTED'
    CANCELLED = 'CANCELLED'


class TaskObj:
    """Define an executed task
    """

    def __init__(self, id: str):
        self.id: str = id
        self.future: Future | None = None
        self.state: str = TaskState.IN_PROGRESS
        self.progress: int = 0  # TODO: make it reportable
        self.error: str | None = None
        self.submission_time: datetime = datetime.now()
        self.completion_time: datetime | None = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'state': self.state,
            'progress': self.progress,
            'error': self.error,
            'submission_time': self.submission_time,
            'completion_time': self.completion_time,
        }


class TaskCreationFailureException(Exception):
    def __init__(self, message: str | None = None, code: int = 0):
        super().__init__()
        self.message: str | None = message
        self.code: int = code


class TaskCancelFailureException(Exception):
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

    def __run_task_wrapper(self,
                           task_id: str,
                           task_func: Callable,
                           reporter_lambda: Callable[[int], None] | None,
                           args: tuple,
                           kwargs: dict):
        """Run given task
        """
        try:
            task_func(*args, **kwargs, reporter=reporter_lambda)
            self.tasks[task_id].state = TaskState.FINISHED
            self.tasks[task_id].completion_time = datetime.now()
            self.tasks[task_id].progress = 100
        except Exception as e:
            self.tasks[task_id].state = TaskState.FAULTED
            self.tasks[task_id].completion_time = datetime.now()
            self.tasks[task_id].error = str(e)

    def __get_active_task_count(self) -> int:
        """Get active task count also cleanup expired tasks
        """
        with self.lock:
            expired: list[str] = list()
            res: int = 0
            for id in self.tasks:
                if self.tasks[id].state == TaskState.IN_PROGRESS:
                    res += 1
                else:
                    completion_time: datetime | None = self.tasks[id].completion_time
                    if completion_time:
                        if (datetime.now() - completion_time).total_seconds() > EXPIRATION_DURATION:
                            expired.append(id)
                    else:
                        expired.append(id)

            for id in expired:
                self.tasks.pop(id)
        return res

    def submit_task(self, task_func: Callable,
                    callback_lambda: Callable | None,
                    report_progress: bool,
                    *args,
                    **kwargs):
        """Submit a function as a concurrent task and executing in the background

        Args:
            task_func (Callable): The function to be executed
            callback_lambda (Callable | None): The optional callback function to be executed after the task is finished
            reporter_lambda (Callable[[TaskObj], None] | None): The optional callback function to be executed to report the task progress
        """
        if self.__get_active_task_count() >= self.max_parallel_tasks:
            raise TaskCreationFailureException('Maximum number of parallel tasks exceeded')

        with self.lock:
            task_id: str = str(uuid.uuid4())
            task: TaskObj = TaskObj(task_id)
            # The reporter lambda is used to report the progress of this task object
            reporter: Callable[[int], None] | None = None
            if report_progress:
                reporter = lambda x: setattr(self.tasks[task_id], 'progress', x)

            future: Future = self.thread_pool.submit(self.__run_task_wrapper, task_id, task_func, reporter, args, kwargs)
            task.future = future
            self.tasks[task_id] = task

        if callback_lambda:
            future.add_done_callback(callback_lambda)
        return task_id

    def cancel_task(self, task_id: str):
        """Cancel an executing task
        """
        if task_id in self.tasks:
            future = self.tasks[task_id].future
            if not future:
                raise TaskCancelFailureException('Task is not running')
            if not future.done():
                future.cancel()
                self.tasks[task_id].state = TaskState.CANCELLED
                self.tasks[task_id].completion_time = datetime.now()

    def get_task_state(self, task_ids: list[str]) -> list[dict | None]:
        """Check the running state of given task IDs
        """
        res: list[dict | None] = list()
        for id in task_ids:
            task: TaskObj | None = self.tasks.get(id, None)
            if task:
                res.append(task.to_dict())
            else:
                res.append(None)
        return res
