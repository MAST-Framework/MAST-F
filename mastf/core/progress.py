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
from celery.app.task import Task, states
from celery.result import AsyncResult

PROGRESS = "PROGRESS"


class Observer:
    """Represents an observer of a task.

    :param task: The task being observed.
    :type task: Task
    :param position: the initial progress position, defaults to 0
    :type position: int, optional
    """

    def __init__(self, task: Task, position: int = 0) -> None:
        self._task = task
        self._pos = abs(position) % 100

    @property
    def task(self) -> Task:
        """Gets the observed task.

        :return: the linked task
        :rtype: Task
        """
        return self._task

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
        total: int = 100,
        state: str = PROGRESS,
        meta: dict = None,
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
            current = self.increment() if increment else self.pos
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

        self.task.update_state(state=state, meta=data)
        return state, meta

    def success(self, msg: str = "", *args) -> tuple:
        """Sets the task state to ``SUCCESS`` and inserts the given message.

        :param msg: the message to format
        :type msg: str
        :return: the updated task state and meta information
        :rtype: tuple
        """
        return self.update(msg, *args, current=100, state=states.SUCCESS)

    def fail(self, msg: str, *args) -> tuple:
        """Sets the task state to ``FALIURE`` and inserts the given message.

        :param msg: the message to format
        :type msg: str
        :return: the updated task state and meta information
        :rtype: tuple
        """
        return self.update(
            msg,
            *args,
            current=100,
            state=states.FAILURE,
            meta={"exc_type": RuntimeError, "exc_message": msg % args},
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
        return self.update(
            msg,
            *args,
            current=100,
            state=states.FAILURE,
            meta={
                "exc_type": type(exception).__name__,
                "exc_message": str(exception),
            },
        )
