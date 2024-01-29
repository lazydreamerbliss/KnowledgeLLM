import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from threading import Event, Lock
from typing import Callable

from utils.exceptions.task_errors import (TaskCancelFailureException,
                                          TaskCreationFailureException)

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
        self.cancel_event: Event | None = None
        self.state: str = TaskState.IN_PROGRESS
        self.progress: int = 0  # TODO: make it reportable
        self.error: str | None = None
        self.submitted_on: datetime = datetime.now()
        self.completed_on: datetime | None = None
        self.duration: int = -1

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'state': self.state,
            'progress': self.progress,
            'error': self.error,
            'submitted_on': self.submitted_on,
            'completed_on': self.completed_on,
            'duration': self.duration,
        }


class TaskRunner:
    def __init__(self, max_parallel_tasks: int = 5):
        self.tasks: dict[str, TaskObj] = dict()
        self.max_parallel_tasks: int = max_parallel_tasks
        self.thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_parallel_tasks)
        self.lock = Lock()

    def __mark_task_completed(self, task_id: str, termination_state: str, error: str | None = None):
        """Mark a task as completed with given state
        """
        if termination_state == TaskState.FINISHED:
            self.tasks[task_id].progress = 100
        now: datetime = datetime.now()
        self.tasks[task_id].state = termination_state
        self.tasks[task_id].completed_on = now
        self.tasks[task_id].error = error
        self.tasks[task_id].duration = int((now - self.tasks[task_id].submitted_on).total_seconds())

    def __run_task_wrapper(self,
                           task_id: str,
                           task_func: Callable,
                           progress_reporter: Callable[[int], None] | None,
                           cancel_event: Event | None,
                           args: tuple,
                           kwargs: dict):
        """Run given task
        """
        try:
            task_func(*args, **kwargs,
                      progress_reporter=progress_reporter,
                      cancel_event=cancel_event)
            self.__mark_task_completed(task_id, TaskState.FINISHED)
        except Exception as e:
            self.__mark_task_completed(task_id, TaskState.FAULTED, str(e))

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
                    completed_on: datetime | None = self.tasks[id].completed_on
                    if completed_on:
                        if (datetime.now() - completed_on).total_seconds() > EXPIRATION_DURATION:
                            expired.append(id)
                    else:
                        expired.append(id)

            for id in expired:
                self.tasks.pop(id)
        return res

    def submit_task(self, task_func: Callable,
                    callback_lambda: Callable | None,
                    support_reporter: bool,
                    support_cancel: bool,
                    *task_args,
                    **task_kwargs):
        """Submit a function as a concurrent task and executing in the background

        Args:
            task_func (Callable): The function to be executed
            callback_lambda (Callable | None): The optional callback function to be executed after the task is finished
            reporter_lambda (Callable[[TaskObj], None] | None): The optional callback function to be executed to report the task progress
                To support this, target function must have a keyword argument named `progress_reporter`
            support_cancel (bool): If the task supports cancellation.
                To support this, target function must have a keyword argument named `cancel_event`
        """
        if self.__get_active_task_count() >= self.max_parallel_tasks:
            raise TaskCreationFailureException('Maximum number of parallel tasks exceeded')

        with self.lock:
            task: TaskObj = TaskObj(str(uuid.uuid4()))
            # The reporter lambda is used to report the progress of this task object
            progress_reporter: Callable[[int], None] | None = None
            if support_reporter:
                progress_reporter = lambda x: setattr(self.tasks[task.id], 'progress', x)
            if support_cancel:
                task.cancel_event = Event()

            future: Future = self.thread_pool.submit(
                self.__run_task_wrapper, task.id, task_func, progress_reporter, task.cancel_event, task_args, task_kwargs)
            task.future = future
            self.tasks[task.id] = task

        if callback_lambda:
            future.add_done_callback(callback_lambda)
        return task.id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel an executing task
        1. Try to stop the future if the task is not started
        2. On failure, check if task supports cancellation
        """
        if task_id in self.tasks:
            future = self.tasks[task_id].future
            if not future:
                raise TaskCancelFailureException('Task is not running')
            if not future.done():
                cancelled: bool = future.cancel()
                if not cancelled and self.tasks[task_id].cancel_event:
                    self.tasks[task_id].cancel_event.set()  # type: ignore
                    cancelled = True
                if cancelled:
                    self.__mark_task_completed(task_id, TaskState.CANCELLED)
                    return True
        return False

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

    def is_task_done(self, task_id: str) -> bool:
        """Check if a task is done
        """
        if task_id in self.tasks:
            return self.tasks[task_id].state != TaskState.IN_PROGRESS
        return False
