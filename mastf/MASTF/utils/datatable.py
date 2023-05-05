from django.http.request import HttpRequest

class DataTableRequest:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self._columns = []
        self._parse()

    @property
    def start(self) -> int:
        return int(self.request.GET.get("start", 0))

    @property
    def length(self) -> int:
        return int(self.request.GET.get("length", 0))

    @property
    def columns(self) -> list:
        return self._columns

    @property
    def search_value(self) -> str:
        return self.request.GET.get("search[value]", "")

    @property
    def order_column(self) -> int:
        return int(self.request.GET.get("order[0][column]", "-1"))

    @property
    def order_direction(self) -> str:
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
