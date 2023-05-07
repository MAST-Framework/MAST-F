# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor, Janbehere1
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
__doc__ = """
Additional middleware classes that intercept requests before any view
can handle them.
"""
from django.shortcuts import render

from mastf.MASTF.models import Environment


class FirstTimeMiddleware:
    """Used to redirect to the setup page when starting this framework
    for the first time.

    Note that this middleware will return a rendered setup page for all
    incoming request if the framework has not been initialized.
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)

        # If it's the first time the app is started and the request is
        # not for the setup wizard, return the setup wizard page (which
        # will guide the user through the initial configuration steps)
        env = Environment.env()
        if env.first_start and request.path != "/api/v1/setup/":
            return render(request, "setup/wizard.html")

        return response
