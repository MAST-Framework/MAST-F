import datetime

from django.db import models
from django.contrib.auth.models import User

from mastf.MASTF.utils.enum import Severity

from .base import Project, File, Team

__all__ = [
    'Scan', 'Scanner', 'ScanTask', 'Details'
]

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

    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    """Stores a relation to the file to scan."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    """The project of this scan"""

    scan_type = models.CharField(null=True, max_length=50)
    """Stores the name of the scan type"""

    start_date = models.DateField(default=datetime.datetime.now)
    """Stores the start time of this scan"""

    end_date = models.DateField(null=True)
    """Stores the ent datetime of the scan"""

    status = models.CharField(null=True, max_length=256)
    """Stores information about the current scan's status"""

    risk_level = models.CharField(default=Severity.NONE, choices=Severity.choices, max_length=256)
    """Stores the classification (LOW, MEDIUM, HIGH)"""

    initiator = models.ForeignKey(User, on_delete=models.CASCADE)
    """Stores the user that has started the scan"""

    is_active = models.BooleanField(default=False)
    """Simple property used to indicate whether the scan is stil busy."""

    finished = models.BooleanField(default=False)
    """Property to determine whether this scan has finished."""

    @staticmethod
    def last_scan(project: Project = None, initiator: User = None):
        """Returns the last scan that was started by the provided user or within the given project.

        :param project: the project the last scan has been started in, defaults to None
        :type project: Project, optional
        :param initiator: the initiator of the last scan, defaults to None
        :type initiator: User, optional
        :return: the last scan instance or None
        :rtype: Scan
        """
        scans = Scan.objects.order_by('start_date')
        if project:
            scans = scans.filter(project=project)

        if initiator:
            scans = scans.filter(initiator=initiator)

        if not project and not initiator:
            scans = [] # !important: we don't want users to access unknown scans

        return scans[0] if len(scans) > 0 else None

    @staticmethod
    def files(project: Project = None, initiator: User = None,
              team: Team = None) -> list:
        """Returns a list of files that have been saved by a given user or within the provided project.

        :param project: the project, defaults to None
        :type project: Project, optional
        :param initiator: the initiator of target scans, defaults to None
        :type initiator: User, optional
        :return: a list of uploaded files
        :rtype: list
        """
        scans = Scan.objects.all()
        if project:
            scans = scans.filter(project=project)

        if initiator:
            scans = scans.filter(initiator=initiator)

        if team:
            scans = scans.filter(project__team=team)

        if not project and not team and not initiator:
            return [] # !important: we don't want users to access unknown files

        return [x.file for x in scans]


class Scanner(models.Model):
    """Simple model to map selected scanners to a scan."""

    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, null=True)
    """Stores a relation to the scan this scanner is used in."""

    name = models.CharField(max_length=256, null=False)
    """Stores a name of the plugin to use."""

    @staticmethod
    def names(project: Project) -> list:
        """Returns a list of names of scanners that are assigned to a project.

        :param project: the target project
        :type project: Project
        :return: a list of selected scanners (only names)
        :rtype: list
        """
        queryset = (Scanner.objects.filter(scan__project=project)
            .values('name')
            .annotate(scount=models.Sum('name'))
        )
        return [getattr(x, "name") for x in queryset]


class ScanTask(models.Model):
    task_uuid = models.UUIDField(max_length=32 ,primary_key=True, null=False)
    scan = models.ForeignKey(Scan, models.CASCADE)
    scanner = models.ForeignKey(Scanner, models.CASCADE, null=True)

    celery_id = models.CharField(max_length=256, null=True)
    active = models.BooleanField(default=True)

    @staticmethod
    def active_tasks(scan: Scan = None, project: Project = None) -> list:
        if scan:
            return ScanTask.objects.filter(active=True, scan=scan)

        if project:
            return ScanTask.objects.filter(active=True, scan__project=project)

        return []


class Details(models.Model):
    scan = models.ForeignKey(Scan, models.CASCADE, null=True)

    cvss = models.FloatField(default=0)
    file = models.ForeignKey(File, models.SET_NULL, null=True)
    tracker_count = models.IntegerField(default=0)
