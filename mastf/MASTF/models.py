import datetime

from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):

    name = models.CharField(max_length=256, null=True)
    """The group's name"""


class File(models.Model):
    '''Stores information about the uploaded file'''

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


class Project(models.Model):

    project_uuid = models.CharField(primary_key=True, null=False, max_length=256)
    """Stores the UUID of this project."""

    name = models.CharField(null=True, max_length=256)
    """Stores the display name of this application."""

    tags = models.CharField(max_length=4096, null=True)
    """Stores tags for this project (comma-spearated)"""

    visibility = models.CharField(max_length=32, null=True)

    risk_level = models.CharField(max_length=16, null=True)

    owner = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    file = models.ForeignKey(File, on_delete=models.DO_NOTHING)


class ProjectGroup(models.Model):

    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    """Stores the group reference."""

    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    """Stores the project reference"""

class ProjectScanner(models.Model):
    
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    scanner = models.CharField(max_length=256, null=True)


class Scan(models.Model):

    scan_uuid = models.CharField(primary_key=True, max_length=256)
    """Stores the identifier for this scan."""

    origin = models.CharField(null=True, max_length=32)
    """Stores the scan origin of the scan.

    The origin can point to the following values:

    - Play-Store
    - iOS-App-Store
    - APKPure
    - File
    """

    source = models.CharField(null=True, max_length=256)
    """Stores the file source.

    The source of an uploaded file can be one of the following:

    - URL: An URL was given from where the file was downloaded
    - File: Simple file upload
    """

    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    """The project of this scan"""

    scan_type = models.CharField(null=True, max_length=50)
    """Stores the name of the scan type"""

    start_date = models.DateField(default=datetime.datetime.now)
    """Stores the start time of this scan"""

    end_date = models.DateField(null=True)
    """Stores the actual duration of the scan"""

    status = models.CharField(null=True, max_length=256)
    """Stores information about the current scan's status"""

    risk_level = models.CharField(null=True, max_length=256)
    """Stores the classification (LOW, MEDIUM, HIGH)"""

    initiator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    """Stores the user that started the scan"""

    is_active = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)


class FindingTemplate(models.Model):
    template_id = models.CharField(max_length=50, null=True)
    title = models.CharField(max_length=256, blank=True)
    description = models.CharField(max_length=4096, blank=True)
    severity = models.CharField(max_length=256, null=True)
    format_keys = models.CharField(max_length=4096, null=True)


class AbstractBaseFinding(models.Model):
    finding_id = models.CharField(max_length=256, blank=True)
    scan = models.ForeignKey(Scan, on_delete=models.DO_NOTHING)

    language = models.CharField(null=True, max_length=256)
    """Specifies the programming language this finding was found in (optional)"""

    severity = models.CharField(max_length=32)
    """Specifies the severity of this finding.

    There are five common severity states:

    - ``INFO``: Used on vulnerabilites that can't be exploited or that are
                just informational
    - ``LOW``: Vulnerabilites that don't have big impact on the application
    - ``MEDIUM``: These vulnerabilitis should be scheduled for removed in the
                  next minor realease
    - ``HIGH``: Important or known issues that can lead to dangerous situations
    - ``CRITICAL``: Verified vulnerabilites that have been marked as ``HIGH``
    """

    source_file = models.CharField(max_length=256, null=True)
    """Returns the relative path to the source code file"""

    source_line = models.CharField(max_length=256, null=True)
    """Stores the lines in the source code that indicate this vulnerability."""

    discovery_date = models.DateField(null=True)
    """Stores the date this vulnerability was detected."""

    scanner = models.CharField(null=True, max_length=256)

    template = models.ForeignKey(FindingTemplate, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        abstract = True


class Finding(AbstractBaseFinding):

    is_custom = models.BooleanField(default=False)


class Vulnerability(AbstractBaseFinding):

    state = models.CharField(null=True, max_length=256)
    """Specifies the state of this vulnerability.

    There are five states by default:

    - ``To Verify``: Identified vulnerabilites that must be verified
    - `'Not Exploitable``: Identified vulnerabilities that can't be exploited
    - ``Proposed Not Exploitable``: this vulnerability is proposed to be not
                                    exploitable
    - ``Confirmed``: The vulnerability has been confirmed
    - ``Urgent``: marked as ``CRITICAL`` and confirmed
    """

    status = models.CharField(null=True, max_length=256)
    """The status of this vulnerability"""


class AccountData(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    is_private = models.BooleanField(default=True)
    avatar = models.ForeignKey(File, on_delete=models.CASCADE)
    role = models.CharField(max_length=256, null=True)


class ScanResult(models.Model):

    scan = models.ForeignKey(Scan, models.DO_NOTHING)
    recurring_results = models.IntegerField(default=0)
    new_results = models.IntegerField(default=0)


class Permission(models.Model):
    permission_uuid = models.UUIDField(primary_key=True)
    identifier = models.CharField(max_length=256, null=False)
    name = models.CharField(max_length=256, null=True)
    protection_level = models.CharField(max_length=256, blank=True)
    dangerous = models.BooleanField(default=False)
    group = models.CharField(max_length=256, null=True)

    short_description = models.CharField(max_length=256, blank=True)
    description = models.CharField(max_length=4096, blank=True)

    source = models.CharField(max_length=512, null=True)
    risk = models.CharField(max_length=8192, null=True)

    def plevel_status(self) -> dict:
        return {'Dangerous': 'red'}


class PermissionFinding(AbstractBaseFinding):
    
    permission = models.ForeignKey(Permission, models.DO_NOTHING)


class Details(models.Model):
    name = models.CharField(max_length=512, null=True)
    scan = models.ForeignKey(Scan, models.DO_NOTHING)
    