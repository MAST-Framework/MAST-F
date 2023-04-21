import logging

from uuid import uuid4
from typing import OrderedDict

from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import (
    authentication, status, permissions
)

logger = logging.getLogger(__name__)

class GetObjectMixin:
    model = None
    """The model used to retrieve instances."""

    lookup_field: str = 'pk'
    """The field that should be used within object lookup"""

    def get_object(self):
        """Returns a project mapped to a given primary key

        :return: the instance of the desired model
        :rtype: ? extends Model
        """
        assert self.model is not None, (
            "The stored model must not be null"
        )

        assert self.lookup_field is not None, (
            "The field used for lookup must not be null"
        )

        assert self.lookup_field in self.kwargs, (
            "Invalid lookup field - not included in args"
        )

        instance = get_object_or_404(
            self.model.objects.all(), **{self.lookup_field: self.kwargs[self.lookup_field]}
        )
        self.check_object_permissions(self.request, instance)
        return instance


class APIViewBase(GetObjectMixin, APIView):
    """Base class for default implementations of an APIView.

    This class implements the behaviour for retrieving, updating
    and removing database model related information. Therefore,
    the following HTTP-methods are implemented:

        - ``GET``: Retrieving instances
        - ``DELETE``: Removing an instance
        - ``PATCH``: Updating single columns
    """

    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        authentication.TokenAuthentication
    ]

    serializer_class = None
    """The serializer used to parse, validate and update data"""


    def get(self, request: Request, *args, **kwargs) -> Response:
        """Returns information about a single object

        :param request: the HttpRequest
        :type request: Request
        :return: the JSON response storing all related data
        :rtype: Response
        """
        instance = self.get_object()

        assert self.serializer_class is not None, (
            "The provided serializer class must not be null"
        )
        data = self.serializer_class(instance)
        return Response(data.data)

    def patch(self, request: Request, *args, **kwargs) -> Response:
        """Updates the selected object.

        :param request: the HttpRequest
        :type request: Request
        :return: whether the data has been updated successfully
        :rtype: Response
        """
        instance = self.get_object()

        assert self.serializer_class is not None, (
            "The provided serializer class must not be null"
        )
        try:
            data = request.data
            serializer = self.serializer_class(instance, data=data, partial=True)
            if serializer.is_valid(): # we must call .is_valid() before .save()
                serializer.save()
            else:
                messages.error(self.request, str(serializer.errors), str(self.serializer_class.__name__))
                return Response(serializer.errors)

        except Exception as err:
            messages.error(self.request, str(err), str(err.__class__.__name__))
            return Response({'err': str(err)}, status.HTTP_400_BAD_REQUEST)

        logger.debug('(%s) Instance-Update: %s', self.__class__.__name__, instance)
        return Response({'success': True})

    def delete(self, request: Request, *args, **kwargs) -> Response:
        """Deletes the selected object.

        :param request: the HttpRequest
        :type request: Request
        :return: permission errors, ``404`` if there is no project with the
                 provided id or ``200`` on success
        :rtype: Response
        """
        instance = self.get_object()
        try:
            self.on_delete(request, instance)
            instance.delete()
        except Exception as err:
            logger.exception("(%s) Delete-Instance: ", self.__class__.__name__)
            messages.error(self.request, str(err), str(err.__class__.__name__))
            return Response({'err': str(err)}, status.HTTP_400_BAD_REQUEST)

        logger.debug('Delete-Instance (success): id=%s', instance.pk)
        return Response({'success': True}, status.HTTP_200_OK)

    def on_delete(self, request: Request, obj) -> None:
        """Gets executed before the provided object will be deleted.

        :param request: the HttpRequest
        :type request: Request
        :param obj: the instance
        :type obj: ? extends Model
        """
        pass


class ListAPIViewBase(ListAPIView):

    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        authentication.TokenAuthentication
    ]

    permission_classes = [permissions.IsAuthenticated]

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        """Filters the queryset before returning the data

        :param queryset: the initial queryset
        :type queryset: QuerySet
        :return: the filtered data
        :rtype: QuerySet
        """
        return queryset


class CreationAPIViewBase(APIView):
    """Basic API-Endpoint to create a new database objects."""

    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        authentication.TokenAuthentication
    ]

    form_class = None
    """The form to use"""

    model = None
    """The database which will be used to create the instance"""

    def post(self, request: Request) -> Response:
        """Creates a new database object.

        :param request: the HttpRequest
        :type request: Request
        :return: any errors relating to the validated object creation form
                 or a success message containing the object's uuid
        :rtype: Response
        """
        form_data = request.data
        if not form_data:
            form_data = request.POST

        form = self.form_class(data=form_data)
        if not form.is_valid():
            logger.warning('Form-Invalid at %s:\n%s', self.request.path, form.errors)
            return Response(form.errors, status.HTTP_400_BAD_REQUEST)

        try:
            instance_id = self.make_uuid()
            data = form.cleaned_data

            data['pk'] = instance_id
            self.set_defaults(request, data)

            instance = self.model.objects.create(**data)
            self.on_create(request, instance)
            logger.debug('(%s) New-Instance: %s', self.__class__.__name__, instance)
        except Exception as err:
            logger.exception("New-Instance")
            messages.error(self.request, str(err), str(err.__class__.__name__))
            return Response({'detail': str(err)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {'success': True, 'pk': str(instance_id)}, status.HTTP_201_CREATED
        )

    def set_defaults(self, request: Request, data: dict) -> None:
        """Sets default values within the final data that creates the intance.

        :param request: the HttpRequest
        :type request: Request
        :param data: the pre-defined data that has been received
        :type data: dict
        """
        pass

    def on_create(self, request: Request, instance) -> None:
        """Called whenever a new instance has been created."""
        pass

    def make_uuid(self):
        """Creates the UUID for a new instance"""
        return uuid4()

