from django.shortcuts import render, redirect
from django.urls import reverse, NoReverseMatch
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from mastf.MASTF.utils.helpers import http_request

from mastf.MASTF.views.api.api_auth import (
    api_login_user,
    api_new_user,
    api_logout_user
)

@http_request(['POST'])
def login_user(request: HttpRequest):
    result = api_login_user(request)
    next_url = request.POST.get("fallback_url", None)
    
    if result.status_code == 200:
        if next_url:
            try:
                return redirect(next_url)
            except NoReverseMatch:
                pass

        return HttpResponseRedirect(reverse('Index'))
    
    messages.error(request, "Invalid username or password")
    if not next_url:
        return HttpResponseRedirect(reverse('SignIn'))
    
    return redirect(f"/login?next={next_url}")

@http_request(['POST'])
def register_user(request: HttpRequest):
    result = api_new_user(request)
    
    if result.status_code == 200:
        messages.info(request, "User added successfully")
        return HttpResponseRedirect(reverse('SignIn'))
    
    if result.status_code == 409:
        messages.error(request, "User with given username already present")
    elif result.status_code == 400:
        messages.error(request, "Invalid username or password too short (min 12 chars)")
        
    return HttpResponseRedirect(reverse('SignUp')) 

@http_request(['POST'])
def logout_user(request: HttpRequest):
    result = api_logout_user(request)
    
    if result.status_code == 200:
        messages.info(request, "Logged out successfully")
    elif result.status_code == 401:
        messages.error(request, "Unauthenticated!")

    return HttpResponseRedirect(reverse('SignIn'))
    

@http_request(['GET'])
def signin_view(request: HttpRequest):
    return render(request, "auth/sign-in.html")

@http_request(['GET'])
def signup_view(request: HttpRequest):
    return render(request, "auth/sign-up.html")
        