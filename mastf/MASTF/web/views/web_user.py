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
# TODO: logout, login, registration (VIEWS)
from django.contrib import messages
from django.urls import reverse, NoReverseMatch
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View

from mastf.MASTF.rest.views import rest_user

__all__ = [
    'LoginView', 'RegstrationView', 'LogoutView'
]

class LoginView(TemplateView):
    template_name = 'auth/sign-in.html'

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Performs a login by calling the REST-API view.

        In addition, this method will perform a redirect to another
        location if specified.

        :param request: the HttpRequest
        :type request: HttpRequest
        :return: a redirect to the next page on success
        :rtype: HttpResponse
        """
        view = rest_user.LoginView.as_view()
        result = view(request)

        callback = request.POST.get('fallback_url', None)
        if callback and result.status_code == 200:
            try:
                callback = callback.removeprefix("http")
                return redirect(callback)
            except NoReverseMatch:
                pass # maybe log that

        if result.status_code == 200:
            return HttpResponseRedirect(reverse('Index'))

        messages.error(request, 'Invalid username or password')
        if not callback:
            return redirect('User-Login')

        return redirect(f"/web/login?next={callback}")


class RegstrationView(TemplateView):
    template_name = 'auth/sign-up.html'

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Registers a new user by calling the REST-API view.

        :param request: the HttpRequest
        :type request: HttpRequest
        :return: a redirect to the login page on success
        :rtype: HttpResponse
        """
        view = rest_user.RegistrationView.as_view()
        result = view(request)

        if result.status_code == 200:
            messages.info(request, 'User added successfully!')
            return HttpResponseRedirect(reverse('User-Login'))

        if result.status_code == 400:
            messages.error(request, 'Invalid form data (internal server error)')

        if result.status_code == 409:
            messages.error(request, 'Username already present or password too short')

        return redirect('User-Registration')


class LogoutView(View):

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Registers a new user by calling the REST-API view.

        :param request: the HttpRequest
        :type request: HttpRequest
        :return: a redirect to the login page on success
        :rtype: HttpResponse
        """
        view = rest_user.LogoutView.as_view()
        result = view(request)

        if result.status_code == 200:
            return redirect('User-Login')

        messages.error(request, 'Could not logout user!')
        return redirect('Index')



