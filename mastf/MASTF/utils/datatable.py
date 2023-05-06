from django.http.request import HttpRequest

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
    ---------------------

    While this class is capable of parsing DataTable requests, it can be used
    within every context having the following parameters in mind:

    - ``column[$idx][data]``: Stores the column name at the specified index
    - ``column[$idx][searchable]``: Indicates whether this column is searchable
    - ``column[$idx][search][value]``: Specifies an extra search value that
                                       should be applied instead of the global
                                       one.
    - ``search[value]``: Global search value
    - ``order[0][column]``: Defines the column that should be ordered in a
                            specific direction
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
                value = self.request.GET.get(f"columns[{index}][search][value]", "") or self.search_value
                if value:
                    query_params[f"{column}__icontains"] = value

            self._columns.append({
                'params': query_params, 'name': column
            })
            index += 1
