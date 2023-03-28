"""File that contains helper methods and classes."""

import functools

from django.http import HttpRequest, HttpResponseNotAllowed

ALLOW_METHODS = [
    'GET', 'POST', 'PUT',
    'DELETE', 'PATCH', 'OPTIONS', 
    'HEAD', 'TRACE'
]

def http_request(allowed_methods: list):
    """Request method checks.

    :param allowed_methods: a list of allowed HTTP request methods
    """
    if (not isinstance(allowed_methods, list) 
            and not isinstance(allowed_methods, tuple)
            and not isinstance(allowed_methods, str)):
        raise ValueError('Invalid type on allowed methods parameter')

    if isinstance(allowed_methods, str):
        methods = [allowed_methods.upper()]
    else:
        methods = [str(x).upper() for x in allowed_methods]

    for method in methods:
        if method not in ALLOW_METHODS:
            raise ValueError('This method is not allowed')

    def prepare_check(func):
        @functools.wraps(func)
        def internal_check(*args, **kwargs):
            # check HTTP-Method and execute wrapped function
            request = None
            for argument in args:
                if isinstance(argument, HttpRequest):
                    request = argument
                    break
            
            if request is None:
                raise ValueError('Could not find matching HttpRequest')
            
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)

            return func(*args, **kwargs)
        return internal_check
    return prepare_check 


def new_error(code: int = 500, title: str = "", description: str = "",
              severity: str = "Medium", color: str = "bg-orange-lt"):
    return {
        "code": code,
        "title": title,
        "description": description,
        "severity": severity,
        "color": color,
    }
    
