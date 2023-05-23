# This file is part of MAST-F's Core API
# Copyright (C) 2023  MatrixEditor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import logging

from celery.app.task import Task, states

PROGRESS = "PROGRESS"
logger = logging.getLogger(__name__)

class Observer:
    """Represents an observer of a task.

    Use this class wihtin a shared_task registered in your celery worker. This
    class enables process tracking, e.g:

    .. code-block:: python
        :linenos:

        @shared_task(bind=True)
        def my_task(self, *args):
            observer = Observer(self)

            if some_condition_to_fail:
                # Fail will set a exception class that is used by celery
                # to report any issue was raised during execution
                status, meta = observer.fail("Condition not accepted!")
                return meta.get("description")

            # Always return the detail string as it will be used later on
            status, meta = observer.succes("Condition passed!")
            return meta.get("description")


    :param task: The task being observed.
    :type task: Task
    :param position: the initial progress position, defaults to 0
    :type position: int, optional
    """

    def __init__(
        self, task: Task, position: int = 0, scan_task=None, _logger: logging.Logger = None
    ) -> None:
        self._task = task
        self._pos = abs(position) % 100
        self._scan_task = scan_task
        self._logger = _logger or logger

    @property
    def task(self) -> Task:
        """Gets the observed task.

        :return: the linked task
        :rtype: Task
        """
        return self._task

    @property
    def logger(self) -> logging.Logger:
        """Gets the underlying logger.

        :return: a linked task logger
        :rtype: Task
        """
        return self._logger

    @logger.setter
    def logger(self, value) -> None:
        self._logger = value

    @property
    def pos(self) -> int:
        """Gets the current position.

        :return: the current progress position
        :rtype: int
        """
        return self._pos

    @pos.setter
    def pos(self, val):
        """Sets the current position to the given value.

        :param val: the new progress position
        :type val: int
        """
        self._pos = val

    def increment(self, val: int = 1) -> int:
        """
        Increments the current position by the given value and returns the updated
        position.

        :param val: The value to increment the current position by, defaults to 1
        :type val: int, optional
        :return: The updated position.
        :rtype: int
        """
        self.pos = self.pos + val
        return self.pos

    def create_meta(self) -> dict:
        """Creates the meta information about the current task state."""
        return {"pending": False}

    def update(
        self,
        msg: str,
        *args,
        current: int = -1,
        increment: bool = True,
        step: int = 1,
        total: int = 100,
        state: str = PROGRESS,
        meta: dict = None,
        do_log: bool = False,
        log_level: str = logging.DEBUG,
    ) -> tuple:
        """Update the current task state.

        This method will add a desciption by applying ``msg % args`` to
        format additional parameters.

        :param msg: the progress message
        :type msg: str
        :param current: the current progress value (optional), defaults to -1
        :type current: int, optional
        :param increment: tells whether the internal counter should be incremented before using it, defaults to True
        :type increment: bool, optional
        :param total: maximum value, defaults to 100
        :type total: int, optional
        :param state: the current state's string representation, defaults to PROGRESS
        :type state: str, optional
        :param meta: additional meta variables, defaults to None
        :type meta: dict, optional
        :return: the new task state and meta information
        :rtype: tuple
        """
        total = abs(total) or 100

        percent: float = 0
        if current == -1:
            current = self.increment(abs(step) or 1) if increment else self.pos
        else:
            self.pos = current % total

        if total > 0:
            percent = (abs(int(current)) / int(total)) * 100
            percent = float(round(percent, 2))

        data = self.create_meta()
        data["description"] = msg % args
        data["current"] = int(current)
        data["total"] = int(total)
        data["percent"] = percent
        if meta and isinstance(meta, dict):
            data.update(meta)

        if self._scan_task and self._scan_task.name:
            data["name"] = self._scan_task.name

        if self.task:
            self.task.update_state(state=state, meta=data)

        if do_log and self._logger:
            self._logger.log(log_level, data["description"])

        return state, data

    def success(self, msg: str = "", *args) -> tuple:
        """Sets the task state to ``SUCCESS`` and inserts the given message.

        :param msg: the message to format
        :type msg: str
        :return: the updated task state and meta information
        :rtype: tuple
        """
        self._finish_scan_task()
        return self.update(
            msg, *args, current=100, state=states.SUCCESS, do_log=True, log_level=logging.INFO
        )

    def fail(self, msg: str, exc_type=RuntimeError, *args) -> tuple:
        """Sets the task state to ``FALIURE`` and inserts the given message.

        :param msg: the message to format
        :type msg: str
        :return: the updated task state and meta information
        :rtype: tuple
        """
        self._finish_scan_task()
        return self.update(
            msg,
            *args,
            current=100,
            state=states.FAILURE,
            meta={
                "exc_type": (exc_type or RuntimeError).__name__,
                "exc_message": msg % args,
            },
            do_log=True,
            log_level=logging.WARNING,
        )

    def exception(self, exception, msg: str, *args) -> tuple:
        """Sets the task state to ``Failure`` and inserts an exception message.

        :param msg: the message to format
        :type msg: str
        :param exception: the exception that was raised
        :type exception: ? extends Exception
        :return: the updated task state and meta information
        :rtype: tuple
        """
        self._finish_scan_task()
        return self.update(
            msg,
            *args,
            current=100,
            state=states.FAILURE,
            meta={
                "exc_type": type(exception).__name__,
                "exc_message": str(exception),
            },
            do_log=True,
            log_level=logging.ERROR,
        )

    def _finish_scan_task(self):
        if self._scan_task:
            self._scan_task.active = False
            self._scan_task.save()
