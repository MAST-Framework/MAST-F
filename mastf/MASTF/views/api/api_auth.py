from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from mastf.MASTF.utils.helpers import http_request
from mastf.MASTF.views.api.api_middleware import api_response
from mastf.MASTF.forms import RegisterUserForm

@http_request(['POST'])
def api_login_user(request: HttpRequest):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    if username and password:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return api_response({'success': True})
    
    # Return an 'invalid login' error message.
    return api_response({'success': False}, code=400)

@http_request(['POST'])
def api_new_user(request: HttpRequest):
    form = RegisterUserForm(request.POST)
    if not form.is_valid():
        return api_response({'success': False}, code=400)
    
    
    if User.objects.filter(username=form.data['username']).exists():
        return api_response({'success': False}, code=409)
    
    User.objects.create_user(form.data['username'], password=form.data['password'])
    return api_response({'success': True})

@http_request(['POST'])
def api_logout_user(request: HttpRequest):
    if not request.user.is_authenticated:
        return api_response({'success': False}, code=401)
    
    logout(request)
    return api_response({'success': True})
