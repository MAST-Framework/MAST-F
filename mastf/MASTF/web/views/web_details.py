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
import json
import os

from django.shortcuts import redirect
from django.contrib import messages

from mastf.MASTF.settings import DETAILS_DIR, ARTICLES
from mastf.MASTF.mixins import ContextMixinBase, TemplateAPIView


class DetailsView(ContextMixinBase, TemplateAPIView):
    """A view for displaying details of a specific item."""

    template_name = "details.html"

    def get_context_data(self, **kwargs):
        """
        Retrieve and prepare the context data for rendering the details view.

        :param kwargs: Additional keyword arguments.
        :return: A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        context['pages'] = ARTICLES

        platform = self.kwargs['platform'].lower()
        name = self.kwargs['name'].lower()

        path = DETAILS_DIR / platform / f"{name}.jsontx"
        if not path.exists():
            messages.warning(self.request, f'Invalid details name: {path}', "FileNotFoundError")
            return context


        if not os.path.commonprefix((path, DETAILS_DIR)).startswith(str(DETAILS_DIR)):
            messages.warning(self.request, f'Invalid path name: {path}', "FileNotFoundError")
            return context

        with open(str(path), "r", encoding="utf-8") as fp:
            # Error handling will be done in dispatch() view
            context["data"] = json.load(fp)

        return context
