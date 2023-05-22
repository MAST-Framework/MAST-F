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
This module covers a class to support JQuery DataTable within the REST
API of this project. It is recommended to use ``apply(...)`` to filter
a specific queryset.

.. important::
    All list views of the REST API support jQuery DataTable requests, so
    sorting, filtering and search will be applied to all of them.

"""
import logging

from django.http.request import HttpRequest
from django.db.models import QuerySet, Q

logger = logging.getLogger(__name__)


class DataTableRequest:
    """Parse jQuery DataTables requests.

    This class provides a convenient way to extract the necessary data from a
    jQuery DataTables request to construct a query for the database. It takes
    the request and creates a list of columns that should be queried/searched:

    .. code-block:: python
        :linenos:

        from django.http import HttpRequest
        from myapp.models import MyModel

        def my_view(request: HttpRequest):
            dt_request = DataTableRequest(request)
            # use the extracted data to perform database queries or other#
            # relevant operations.

    In general, the extracted column data will be stored with the following
    structure:

    >>> dt_request = DataTableRequest(request)
    >>> dt_request.columns
    [{'name': "Column1", 'params': {...}}, ...]

    Note that the params dictionary can be used in Django's database queries
    directly by just passing ``**column["params"]``.

    HttpRequest Structure
    ~~~~~~~~~~~~~~~~~~~~~

    While this class is capable of parsing DataTable requests, it can be used
    within every context having the following parameters in mind:

    - ``column[$idx][data]``: Stores the column name at the specified index
    - ``column[$idx][searchable]``: Indicates whether this column is searchable
    - ``column[$idx][search][value]``: Specifies an extra search value that should be applied instead of the global one.
    - ``search[value]``: Global search value
    - ``order[0][column]``: Defines the column that should be ordered in a specific direction
    - ``order[0][dir]``: The sorting direction
    - ``start``: offset position where to start
    - ``length``: preferred data length to return
    """

    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self._columns = []
        self._parse()

    @property
    def start(self) -> int:
        """Defines the starting pointer.

        :return: an integer pointing to the starting offset position
        :rtype: int
        """
        return int(self.request.GET.get("start", 0))

    @property
    def length(self) -> int:
        """Defines the preferred return size.

        :return: an integer or ``0`` if this parameter is not present.
        :rtype: int
        """
        return int(self.request.GET.get("length", 0))

    @property
    def columns(self) -> list:
        """Specifies all column data that is present within this request.

        :return: a list of column structures.
        :rtype: list
        """
        return self._columns

    @property
    def search_value(self) -> str:
        """Defines a global search value

        :return: _description_
        :rtype: str
        """
        return self.request.GET.get("search[value]", "")

    @property
    def order_column(self) -> int:
        """The column index which points to a column that should be ordered.

        :return: ``-1`` if no column is selected ot the column index
        :rtype: int
        """
        return int(self.request.GET.get("order[0][column]", "-1"))

    @property
    def order_direction(self) -> str:
        """Specifies the order direction.

        :return: the direction as string (either ``asc`` or ``desc``)
        :rtype: str
        """
        return self.request.GET.get("order[0][dir]", "desc")

    def _parse(self):
        index = 0
        while True:
            column = self.request.GET.get(f"columns[{index}][data]", None)
            if not column:
                break

            query_params = {}
            if self.request.GET.get(f"columns[{index}][searchable]", True):
                value = (
                    self.request.GET.get(f"columns[{index}][search][value]", "")
                    or self.search_value
                )
                if value:
                    query_params[f"{column}__icontains"] = value

            self._columns.append({"params": query_params, "name": column})
            index += 1


def apply(request: DataTableRequest, queryset: QuerySet) -> QuerySet:
    """Utility function that applies filters or ordering to a Django queryset
    based on a :class:`DataTableRequest` object.

    This function can be used in conjunction with Django's generic views and
    the DataTables jQuery plugin to create dynamic data tables with server-side
    filtering, sorting, and pagination. Simply pass the DataTableRequest object
    and the queryset to this function in your view's ``get_queryset(...)`` method,
    and return the result (or a pageinated one).

    For example, to use this function with the Django ListView, you could define
    your view like this:

    .. code-block:: python
        :linenos:

        from django.views.generic import ListView
        from mastf.MASTF.models import MyModel
        from mastf.MASTF.utils import datatable

        class MyListView(ListView):
            model = MyModel
            template_name = "my_template.html"

            def get_queryset(self):
                request = datatable.DataTableRequest(self.request)
                queryset = super().get_queryset()
                return datatable.apply(request, queryset)

    To use your defined view within a jQuery DataTable, you should set the following
    parameters:

    .. code-block:: javascript+django

        var options = {
            "processing": true,
            "serverSide": true,
            "ajax": {
                // assuming the view is mapped to an URL path with name=MyListView
                "url": "{% url 'MyListView' %}",
                "dataSrc": function(json) {
                    return json.results;
                },
            },
            "columns": {
                {"data": "mycolumn"},
                // ...
            }
        };
        $(element).DataTable(options);

    :param request: a :class:`DataTableRequest` object containing information
                    about the current data table view, such as search keywords,
                    sorting column, and pagination.
    :type request: :class:`DataTableRequest`
    :param queryset: the queryset to apply the filters and ordering to.
    :type queryset: QuerySet
    :return: A filtered and/or ordered queryset based on the DataTableRequest object.
    :rtype: QuerySet
    """
    model = queryset.model
    query: Q = None
    for column in request.columns:
        if not hasattr(model, column["name"]):
            logger.debug(f'Skipped column definition: {column["name"]}')
            continue

        next_query = Q(**column["params"])
        if not query:
            query = next_query
        else:
            query = next_query | query

    queryset = queryset.filter(query) if query else queryset
    order_column = request.order_column
    if order_column != -1:
        order_column = request.columns[order_column]["name"]
        if not hasattr(queryset.model, order_column):
            logger.debug(
                f"Switching non-existend order-column '{order_column}' to 'pk'"
            )
            order_column = "pk"

        if str(request.order_direction).lower() == "desc":
            order_column = f"-{order_column}"

        queryset = queryset.order_by(order_column)
    else:
        queryset = queryset.order_by("pk")

    return queryset