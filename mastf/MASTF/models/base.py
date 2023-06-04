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
import pathlib

from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User

from mastf.MASTF import settings
from mastf.MASTF.utils.enum import Visibility, Severity, InspectionType, Role

# As we're importing all classes and variables within the '__init__'
# file, this statement is needed to cleanup accessabe members.
__all__ = [
    "namespace",
    "Team",
    "Project",
    "File",
    "Account",
    "Bundle",
    "Environment",
    "TimedModel",
]


class namespace(dict):
    """Simple class that stores its attributes in a separate dict.

    It behaves like a normal dictionary with variable assignment possible. So,
    for example:

    >>> var = namespace(foo="bar")
    >>> var.foo
    'bar'

    Variables can still be defined after the object has been created:

    >>> var = namespace()
    >>> var.bar = 2
    >>> var
    {"bar": 2}
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __setattr__(self, __name: str, __value) -> None:
        self[__name] = __value

    def __getattribute__(self, __name: str):
        if __name in self:
            return self[__name]
        # We need the super() call as some special bound
        # methods are not stored in our dictionary.
        return super().__getattribute__(__name)


class TimedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


############################################################
# Django Models
############################################################
class Team(TimedModel):
    """A team contains a set of users.

    .. note::
        We rather use 'Team' as class name than 'Group' as a group class is
        already defined by Django. Each team can have a list of users.

    .. list-table::
        :header-rows: 0
        :widths: 50, 50

        * - Serializer Class
          - :class:`TeamSerializer`
        * - Form Class
          - :class:`TeamForm`
        * - REST Views
          - :class:`TeamView`, :class:`TeamListView` and :class:`TeamCreationView`
    """

    name = models.CharField(max_length=256, null=False, unique=True)
    """The team's name"""

    users = models.ManyToManyField(User, related_name="teams")
    """A ``many-to-many`` relation that simulates a membership in a team"""

    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    """The owner of this team (the user that created the team)"""

    visibility = models.CharField(
        default=Visibility.PRIVATE, choices=Visibility.choices, max_length=256
    )
    """The team's visibility.

    Note that internal should not be applied to teams as this state
    is related to projects.
    """

    @staticmethod
    def get(owner: User, name: str) -> "Team":
        """Returns the first team that stores the given name of the provided user.

        :param owner: the owner or member of a team
        :type owner: User
        :param name: the team's name
        :type name: str
        :return: the first occurrence or None
        :rtype: Team
        """
        query = models.Q(owner=owner, name=name) | models.Q(
            visibility=Visibility.PUBLIC, name=name
        )
        return Team.objects.filter(query).first()

    @staticmethod
    def get_by_owner(owner: User, queryset=None) -> models.QuerySet:
        """Returns all teams in the scope of that user.

        :param owner: the team owner or member
        :type owner: User
        :param queryset: üre-defined collection of teams, defaults to None
        :type queryset: QuerySet, optional
        :return: all teams the given user is a member or the owner of
        :rtype: models.QuerySet
        """
        query = models.Q(owner=owner) | models.Q(users__pk=owner.pk)
        return (queryset or Team.objects).filter(query)


class Project(TimedModel):
    """Database model for mobile application projects.

    .. note::
        Projects may be assigned to whole teams instead of set only one user in
        charge of it. All users that are a member of the project's team are able
        to modify the project.

    This model class also defines utility methods that can be used to retrieve
    the local system path of the project directory as well as general stats that
    will be mapped in a :class:`namespace` object.
    """

    project_uuid = models.CharField(primary_key=True, null=False, max_length=256)
    """Stores the UUID of this project."""

    name = models.CharField(blank=True, max_length=256, unique=True)
    """Stores the display name of this application."""

    tags = models.CharField(max_length=4096, blank=True)
    """Stores tags for this project (comma-spearated)"""

    visibility = models.CharField(
        default=Visibility.PRIVATE, choices=Visibility.choices, max_length=256
    )
    """Stores the visibility of this project."""

    risk_level = models.CharField(
        default=Severity.INFO, choices=Severity.choices, max_length=256
    )
    """Stores the current risk level (bound to severity types)"""

    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    """Specifies the onwer of this project.

    This field my be null as projects can be assigned to whole teams.
    """

    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
    """Specifies the owner of this project. (may be null)"""

    inspection_type = models.CharField(
        default=InspectionType.SIMPLE, choices=InspectionType.choices, max_length=256
    )
    """Specifies the inspection type to apply when scanning an app."""

    @staticmethod
    def stats(owner: User) -> namespace:
        """Collects information about a project a user can edit.

        :param owner: the project owner
        :type owner: User
        :return: a dictionary covering general stats (count, risk levels)
        :rtype: namespace
        """
        projects = Project.get_by_user(owner)
        data = namespace(count=len(projects))

        data.risk_high = len(projects.filter(risk_level=Severity.HIGH))
        data.risk_medium = len(projects.filter(risk_level=Severity.MEDIUM))
        # The project IDs can be used later on in order to prevent a user to
        # create the previous query again.
        data.ids = set([x.project_uuid for x in projects])
        return data

    @staticmethod
    def get_by_user(owner: User, queryset: models.QuerySet = None) -> models.QuerySet:
        """Returns all projects where the provided user has access to.

        This query attempts to collect all projects that can be modified by the given
        owner. That includes projects that are assigned to a team of which the provided
        user is a member; projects that are public and projects that are maintained by
        the given owner.

        .. note::
            Only projects that are globally PUBLIC and not assigned to any team will be
            included in this list.

        :param owner: the owner or member
        :type owner: User
        :param queryset: pre-defined project collection, defaults to None
        :type queryset: models.QuerySet, optional
        :return: all projects that fit the requirements
        :rtype: models.QuerySet
        """
        query = (
            models.Q(owner=owner)
            | models.Q(team__users__pk=owner.pk)
            | models.Q(visibility=Visibility.PUBLIC, team=None)
        )
        return (queryset or Project.objects).filter(query)

    @property
    def directory(self) -> pathlib.Path:
        """Returns the project's directory.

        :return: the directory as ``Path`` object.
        :rtype: pathlib.Path
        """
        return settings.PROJECTS_ROOT / str(self.project_uuid)

    def dir(self, path: str, create: bool = True) -> pathlib.Path:
        """Returns the directory at the specified location.

        :param path: the local directory name
        :type path: str
        :param create: whether the directory should be created, defaults to True
        :type create: bool, optional
        :return: the created path instance
        :rtype: pathlib.Path
        """
        directory = self.directory / str(path)
        if create and not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
        return directory


class File(TimedModel):
    """Stores information about the uploaded file.

    Note that this model will store information about the uploaded files only;
    extracted files will be ignored. Each time a scan file is uploaded, it will
    be saved in the projects directory
    """

    md5 = models.CharField(max_length=32, default="", primary_key=True)
    """The identifier for each app (MD5 of uploaded file)"""

    sha256 = models.CharField(max_length=64, default="")
    """Additional hash value"""

    sha1 = models.CharField(max_length=40, default="")
    """Additional hash value"""

    file_name = models.CharField(max_length=256, default="")
    """The file name of the uploaded file."""

    file_size = models.CharField(max_length=50, default="")
    """The available disk space needed to save the uploaded file"""

    file_path = models.CharField(max_length=2048, blank=True)
    """Stores the internal file path. (will be localized separately)"""

    internal_name = models.CharField(max_length=32, default="")
    """Specifies the uploaded file name."""

    @staticmethod
    def relative_path(path: str) -> str:
        # assert that the path contains the "projects" directive
        if not isinstance(path, str):
            path = str(path)

        idx = path.find("projects")
        assert idx != -1, "Invalid path %s: Needed an absolute path" % path

        sub_path = path[idx + len("projects") + 1 :]
        return "/".join(sub_path.split("/")[2:])


class Account(TimedModel):
    """
    Represents an account associated with a user in the system.

    :param user: ForeignKey to the User model representing the user that owns
                 this account.
    :type user: User
    :param role: The role assigned to this account. One of the choices
                 available in the Role enumeration. Defaults to Role.REGULAR.
    :type role: str
    :param description: Optional description for this account.
    :type description: str | None
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=256, choices=Role.choices, default=Role.REGULAR)
    description = models.CharField(max_length=256, blank=True)


class Bundle(TimedModel):
    """
    The ``Bundle`` class represents a collection of projects that belong to a single
    owner. Each bundle can be assigned a risk level and can have multiple tags to
    help with organization.
    """

    bundle_id = models.UUIDField(primary_key=True)
    """A UUID field that serves as the primary key for a bundle instance."""

    name = models.CharField(max_length=256, null=False, unique=True)
    """
    A string field that stores the name of the bundle. It has a maximum length of 256
    characters and is required.
    """

    tags = models.TextField(blank=True)
    """
    A text field that stores tags associated with the bundle. It is optional and
    can be left blank.
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    """A foreign key to the User model that represents the owner of the bundle."""

    risk_level = models.CharField(
        default=Severity.NONE, choices=Severity.choices, max_length=32
    )
    """
    A string field that stores the risk level associated with the bundle. It has a
    default value of ``Severity.NONE``.
    """

    projects = models.ManyToManyField(Project, related_name="bundles")
    """
    A many-to-many field that connects the bundle to the :class:`Project` model and allows
    multiple projects to be associated with a single bundle.
    """

    @staticmethod
    def stats(owner: User) -> namespace:
        """
        This method takes a User instance and returns a namespace object that
        contains statistics about the bundles owned by that user. The namespace
        object contains the following fields:

        - ``count``: The total number of bundles owned by the user.
        - ``risk_high``: The number of bundles with a risk level of Severity.HIGH.
        - ``risk_medium``: The number of bundles with a risk level of Severity.MEDIUM.
        - ``ids``: A set of UUIDs representing the IDs of all the bundles owned by the user.

        :param owner: the owner
        :type owner: User
        :return: a namespace containing stats about the queried bundles.
        :rtype: :class:`namespace`
        """
        bundles = Bundle.get_by_owner(owner)

        data = namespace(count=len(bundles))
        data.count = len(bundles)
        data.risk_high = len(bundles.filter(risk_level=Severity.HIGH))
        data.risk_medium = len(bundles.filter(risk_level=Severity.MEDIUM))
        data.ids = set([x.bundle_id for x in bundles])
        return data

    @staticmethod
    def get_by_owner(owner: User, queryset: models.QuerySet = None) -> models.QuerySet:
        """
        This method takes a User instance and an optional QuerySet instance and returns a
        QuerySet containing all bundles that can be modified by the provided owner. This
        includes bundles that are assigned to a team of which the provided user is a member,
        public bundles, and bundles maintained by the provided owner. If a QuerySet instance
        is provided, the method will apply the filter to that queryset.

        :param owner: the bundle owner
        :type owner: User
        :param queryset: the initial queryset to use, defaults to None
        :type queryset: models.QuerySet, optional
        :return: the filtered queryset
        :rtype: models.QuerySet
        """
        # @ImplNote: Projects which are invisible by default may be included
        # within this query. As bundles try to visualize data of the assigned
        # projects, private projects may be shared throughout a team.
        query = (
            models.Q(projects__owner=owner)
            | models.Q(projects__team__users__pk=owner.pk)
            | models.Q(projects__visibility=Visibility.PUBLIC, projects__team=None)
            | models.Q(owner=owner)
        )
        if not queryset:
            queryset = Bundle.objects.all()

        return queryset.filter(query)


class Environment(TimedModel):
    """
    The ``Environment`` class is a Django model representing the configuration of the
    application's environment.
    """

    env_id = models.UUIDField(primary_key=True)
    """
    A UUIDField attribute that serves as the primary key of the model. It uniquely
    identifies the environment instance.
    """

    allow_registration = models.BooleanField(default=True)
    """
    A boolean attribute that determines whether new user registration is allowed in the
    current environment. The default value is ``True``.
    """

    allow_teams = models.BooleanField(default=True)
    """
    A boolean attribute that determines whether teams are allowed in the environment.
    The default value is ``True``.
    """

    max_projects = models.IntegerField(default=100000)
    """Specifies the maximum number of projects allowed in the environment."""

    max_teams = models.IntegerField(default=10000)
    """Defines the maximum number of teams allowed in the environment"""

    max_bundles = models.IntegerField(default=10000)
    """Defines the maximum number of bundles allowed in the environment."""

    first_start = models.BooleanField(default=True)
    """Indicates whether the application is starting up for the first time."""

    @staticmethod
    def env() -> "Environment":
        """A static method that returns the environment instance.

        If an instance is not found, a new one is created with a unique UUID. This
        method returns the only instance of the Environment model.

        :return: the current environment instance
        :rtype: ``Environment``
        """
        queryset = Environment.objects.first()
        if not queryset:
            return Environment.objects.create(env_id=uuid4())

        return queryset
