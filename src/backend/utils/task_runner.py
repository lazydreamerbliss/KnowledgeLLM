import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from threading import Event
from typing import Callable

from utils.exceptions.task_errors import *

EXPIRATION_DURATION = 86400  # Automatically cleanup finished tasks after these seconds


def report_progress(progress_reporter: Callable[[int, int, str | None], None] | None,
                    current_progress: int,
                    current_phase: int = 1,
                    phase_name: str | None = None):
    """Report the progress of current task
    """
    if not progress_reporter:
        return
    if current_progress is None or current_progress < 0 or current_progress > 100:
        return
    try:
        progress_reporter(current_progress, current_phase, phase_name)
    except BaseException:
        pass


class TaskState:
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'
    FAULTED = 'FAULTED'
    CANCELLED = 'CANCELLED'


class TaskObj:
    """Define an executed task
    """

    def __init__(self, id: str):
        self.future: Future | None = None
        self.cancel_event: Event | None = None
        self.id: str = id
        self.state: str = TaskState.IN_PROGRESS
        self.phase_count: int = 1  # The number of phases in the task
        self.phase_name: str | None = None
        self.current_phase: int = 1
        self.progress: int = 0  # The progress of the task on current phase, if task with 1 phase only then it represents the overall progress of the task
        self.error: str | None = None
        self.submitted_on: datetime = datetime.now()
        self.completed_on: datetime | None = None
        self.duration: int = -1

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'state': self.state,
            'phase_count': self.phase_count,
            'phase_name': self.phase_name,
            'current_phase': self.current_phase,
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
        self.__thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_parallel_tasks)

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

    def __run_task_with_catch(self,
                              task_id: str,
                              task_func: Callable,
                              progress_reporter: Callable | None,
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

    def submit_task(self,
                    task_func: Callable,
                    callback_lambda: Callable | None,
                    support_reporter: bool,
                    support_cancel: bool,
                    phase_count: int,
                    *task_args,
                    **task_kwargs):
        """Submit a function as a concurrent task and executing in the background

        Args:
            task_func (Callable): The target function to be executed
            callback_lambda (Callable | None): The optional callback function to be executed after the task is finished
            support_reporter (bool): If the task supports reporting execution progress
                To support this, target function must have a keyword argument named `progress_reporter`
            support_cancel (bool): If the task supports cancellation
                To support this, target function must have a keyword argument named `cancel_event`
            phase_count (int): The number of phases in the task, used with progress reporter
            task_args (tuple): The positional arguments to be passed to the target function
            task_kwargs (dict): The keyword arguments to be passed to the target function
        """
        if self.__get_active_task_count() >= self.max_parallel_tasks:
            raise TaskCreationFailureException('Maximum number of parallel tasks exceeded')

        task: TaskObj = TaskObj(str(uuid.uuid4()))
        task.phase_count = phase_count if phase_count >= 1 else 1
        if support_cancel:
            task.cancel_event = Event()

        if support_reporter:
            # The reporter function is used to report the progress of current task object via closure
            def progress_reporter(progress: int,
                                  current_phase: int = 1,
                                  phase_name: str | None = None):
                t: TaskObj = self.tasks[task.id]
                t.progress = progress
                t.current_phase = current_phase
                t.phase_name = phase_name
                t.duration = int((datetime.now() - t.submitted_on).total_seconds())
            future: Future = self.__thread_pool.submit(
                self.__run_task_with_catch, task.id, task_func, progress_reporter, task.cancel_event, task_args, task_kwargs)
        else:
            future: Future = self.__thread_pool.submit(
                self.__run_task_with_catch, task.id, task_func, None, task.cancel_event, task_args, task_kwargs)
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

    def get_task_state(self, task_id: str) -> TaskObj | None:
        """Check the running state of given task IDs
        """
        return self.tasks.get(task_id, None)

    def is_task_done(self, task_id: str) -> bool:
        """Check if a task is done, this includes all termination states like cancel, failure, etc.
        """
        if task_id in self.tasks:
            return self.tasks[task_id].state != TaskState.IN_PROGRESS
        return True

    def is_task_successful(self, task_id: str) -> bool:
        """Check if a task is done and successful
        """
        if task_id in self.tasks:
            return self.tasks[task_id].state == TaskState.FINISHED and not self.tasks[task_id].error
        return True
