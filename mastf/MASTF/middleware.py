from django.shortcuts import render

from mastf.MASTF.models import Environment


class FirstTimeMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)

        env = Environment.env()
        if env.first_start and request.path != '/api/v1/setup/':
            return render(request, "setup/wizard.html")

        return response