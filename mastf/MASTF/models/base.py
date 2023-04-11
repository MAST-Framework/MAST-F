import pathlib

from django.db import models
from django.contrib.auth.models import User

from mastf.MASTF import settings
from mastf.MASTF.utils.enum import Visibility, Severity, InspectionType

# As we're importing all classes and variables within the '__init__'
# file, this statement is needed to cleanup accessabe members.
__all__ = [
    'namespace',
    'Team',
    'Project',
    'File',
    'Account',
    
    'VISIBILITY_CHOICES',
    'RISK_CHOICES',
    'INSPECTION_TYPE_CHOICES',
]

class namespace(dict):
    """Simple class that stores its attributes in a separate dict.
    
    It behaves like a normal dictionary with variable assignment possible. So, 
    for example:
    
    >>> var = namespace(foo="bar")
    >>> var.foo
    'bar'
    
    Variables can still be defined after the object has been created. 
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

############################################################
# Django Models
############################################################
VISIBILITY_CHOICES = [(str(x), str(x)) for x in Visibility]
"""Default visbility options for projects"""

RISK_CHOICES = [(str(x), str(x)) for x in Severity]
"""Default risk level choices"""

INSPECTION_TYPE_CHOICES = [(str(x), str(x)) for x in InspectionType]
"""Default inspection type choices"""


class Team(models.Model):
    """A team contains a set of users.

    Note: We rather use 'Team' as class name than 'Group' as a group
    class is already defined by Django. Each team can have a list of
    users.
    """
    
    name = models.CharField(max_length=256, null=False)
    """The team's name"""
    
    users = models.ManyToManyField(User, related_name='teams')
    """A ``many-to-many`` relation that simulates a membership in a team"""
    
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    """The owner of this team (the user that created the team)"""
    
    visibility = models.CharField(default=Visibility.PUBLIC, choices=VISIBILITY_CHOICES, max_length=256)
    """The team's visibility.
    
    Note that internal should not be applied to teams as this state 
    is related to projects.
    """

    @staticmethod
    def get(owner: User, name: str) -> 'Team':
        query = models.Q(owner=owner, name=name) | models.Q(visibility=Visibility.PUBLIC, name=name)
        return Team.objects.filter(query).first()

class Project(models.Model):
    """Database model for mobile application projects.
    
    .. info::
        Projects may be assigned to whole teams instead of set only one user in 
        charge of it. All users that are a member of the project's team are able
        to modify the project.
        
    This model class also defines utility methods that can be used to retrieve 
    the local system path of the project directory as well as general stats that
    will be mapped in a ``namespace`` object.
    """
    
    project_uuid = models.CharField(primary_key=True, null=False, max_length=256)
    """Stores the UUID of this project."""

    name = models.CharField(null=True, max_length=256)
    """Stores the display name of this application."""

    tags = models.CharField(max_length=4096, null=True)
    """Stores tags for this project (comma-spearated)"""

    visibility = models.CharField(default=Visibility.PRIVATE, choices=VISIBILITY_CHOICES, max_length=256)
    """Stores the visibility of this project."""

    risk_level = models.CharField(default=Severity.INFO, choices=RISK_CHOICES, max_length=256)
    """Stores the current risk level (bound to severity types)"""

    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    """Specifies the onwer of this project.
    
    This field my be null as projects can be assigned to whole teams.
    """
    
    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
    """Specifies the owner of this project. (may be null)"""

    inspection_type = models.CharField(default=InspectionType.SIMPLE, choices=INSPECTION_TYPE_CHOICES, max_length=256)
    """Specifies the inspection type to apply when scanning an app."""
    

    @staticmethod
    def stats(owner: User) -> namespace:
        """Collects information about a project a user can edit.

        :param owner: the project owner
        :type owner: User
        :return: a dictionary covering general stats (count, risk levels)
        :rtype: namespace
        """
        
        # This query attempts to collect all projects that can be modified by
        # the given owner. That includes projects that are assigned to a team
        # of which the provided user is a member; projects that are public and 
        # projects that are maintained by the provided owner. 
        # @ImplNote: Only projects that are globally PUBLIC and not assigned to 
        # any team will be included in this list.
        query = (models.Q(owner=owner) | models.Q(team__users__pk=owner.pk)
            | models.Q(visibility=Visibility.PUBLIC, team=None)
        )
        projects = Project.objects.filter(query)
        data = namespace(count=len(projects))

        data.risk_high = len(projects.filter(risk_level=Severity.HIGH))
        data.risk_medium = len(projects.filter(risk_level=Severity.MEDIUM))
        # The project IDs can be used later on in order to prevent a user to 
        # create the previous query again.
        data.ids = [x.project_uuid for x in projects]
        return data

    @property
    def directory(self) -> pathlib.Path:
        """Returns the project's directory.

        :return: the directory as ``Path`` object.
        :rtype: pathlib.Path
        """
        return settings.MASTF_PROJECTS_DIR / str(self.project_uuid)
    
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


class File(models.Model):
    '''Stores information about the uploaded file.
    
    Note that this model will store information about the uploaded files only;
    extracted files will be ignored. Each time a scan file is uploaded, it will
    be saved in the projects directory
    '''

    md5 = models.CharField(max_length=32, default='', primary_key=True)
    '''The identifier for each app (MD5 of uploaded file)'''

    sha256 = models.CharField(max_length=64, default='')
    '''Additional hash value'''

    sha1 = models.CharField(max_length=40, default='')
    '''Additional hash value'''

    file_name = models.CharField(max_length=256, default='')
    '''The file name of the uploaded file.'''

    file_size = models.CharField(max_length=50, default='')
    '''The available disk space needed to save the uploaded file'''

    file_path = models.CharField(max_length=2048, null=True)
    """Stores the internal file path. (will be localized separately)"""
    
    internal_name = models.CharField(max_length=32, default='')
    """Specifies the uploaded file name."""


class Account(models.Model): # unused
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=256, null=True)