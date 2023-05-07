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
The 'serializer' module provides additional functionality to Django REST
framework's serializer classes by adding the :class:`ManyToManyField` and
:class:`ManyToManySerializer` classes.

It offers a :class:`ManyToManyField` class that allows for the serialization
and deserialization of many-to-many relationships, which are commonly used in
Django models. The :class:`ManyToManyField` class supports the full range of
many-to-many fields, including fields with intermediate models and related
objects.

In addition, this module provides a 'ManyToManySerializer' class that can be
used as a base class for serializers that handle many-to-many relationships.
It is designed to simplify the creation of custom serializers with many-to-many
fields.

Let's take a quick look at the following example:

.. code-block:: python
    :linenos:

    from mastf.MASTF.serializers import ManyToManySerializer, ManyToManyField

    # Define a new class with many-to-many relationships
    class BlogSerializer(ManyToManySerializer):
        rel_fields = ("articles", )
        articles = ManyToManyField(Article, mapper=int)

        class Meta:
            model = Blog
            fields = '__all__'

Here, we've created a new class named *BlogSerializer* that uses a
:class:`ManyToManyField` to represent a many-to-many relationships. In
addition, we delcared a ``mapper`` function that will convert incoming
data to the preferred primary key attribute.
"""
from .base import *

from .ser_finding import *
from .ser_scan import *
from .ser_host import *
