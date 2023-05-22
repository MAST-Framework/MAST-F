# This file is part of MAST-F's Frontend API
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
__doc__ = """
Module that stores all important database models plus utility methods
whithin each class. For details on scan related models, please view
one of the following sites:

:doc:`Project and Team related models <base_models>`
    Learn about basic database models required for the web-frontend to work.

:doc:`Basic Scan Models <scan_models>`
    Detailed overview of scan related models including :class:`ScanTask` and
    :class:`Scanner`.

:doc:`Finding Models <finding_models>`
    A list of classes that are used to represent API findings and vulnerabilities
    internally.

:doc:`Permission Models <permission_models>`
    Important app-permission models, **not** user permission models.

:doc:`Package Models <package_models>`
    Explore database models for software packages and dependencies

:doc:`Host Models <host_models>`
    Detailed overview of connection models, hosts, and other related data.

Each class will illustrate what serializers, forms and permission classes are associated
with it. In addition, most database models provide examples and detailed field explainations
in order to provide a detailed overview to them.
"""
from .base import *

from .mod_scan import *
from .mod_finding import *
from .mod_permission import *
from .mod_package import *
from .mod_host import *
from .mod_component import *
