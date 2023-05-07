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
Django forms provide a convenient way to handle user input and data validation.
In this project's context, forms will allow us to receive data from clients
through REST API endpoints and to validate it before we create new objects in
our database.

In order to enhance the capabilities of Django Forms there are implementations
of ``ModelField`` and ``ManyToManyField`` as fields for form classes.
"""

from .base import *

from .form_package import *
from .form_finding import *
from .form_scan import *
from .form_host import *
