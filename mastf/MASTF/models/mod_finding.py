import uuid

from django.db import models
from django.contrib.auth.models import User

from mastf.MASTF.utils.enum import Severity, State, Visibility

from .base import Project, namespace, Team
from .mod_scan import Scan, Scanner

__all__ = [
    'STATE_CHOICES', 'FindingTemplate', 'Snippet',
    'AbstractBaseFinding', 'Finding', 'Vulnerability'
]

STATE_CHOICES = [(str(x), str(x)) for x in State]

class FindingTemplate(models.Model):
    template_id = models.CharField(max_length=128, null=True)
    title = models.CharField(max_length=256, blank=True)
    description = models.TextField()
    default_severity = models.CharField(default=Severity.NONE, choices=Severity.choices, max_length=256)
    risk = models.TextField()
    mitigation = models.TextField()
    article = models.CharField(max_length=256, null=True)

    @staticmethod
    def make_uuid(*args) -> str:
        return f"FT-{uuid.uuid4()}-{uuid.uuid4()}"


class Snippet(models.Model):
    lines = models.CharField(max_length=2048, blank=True)
    """Stores lines that should be highlighted."""

    sys_path = models.CharField(max_length=1024, null=True)
    language = models.CharField(max_length=32, null=True)
    """Specifies the programming language this finding was found in (optional)"""

    file_name = models.CharField(max_length=512, null=True)
    file_size = models.CharField(max_length=256, null=True)


class AbstractBaseFinding(models.Model):
    finding_id = models.CharField(max_length=256, null=False, primary_key=True)
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, null=True)
    snippet = models.ForeignKey(Snippet, on_delete=models.SET_NULL, null=True)

    severity = models.CharField(default=Severity.NONE, choices=Severity.choices, max_length=256)
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

    discovery_date = models.DateField(null=True)
    """Stores the date this vulnerability was detected."""

    scanner = models.ForeignKey(Scanner, on_delete=models.SET_NULL, null=True)
    template = models.ForeignKey(FindingTemplate, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True

    @staticmethod
    def stats(model, member: User = None, project: Project = None, scan: Scan = None,
              team: Team = None, base=None) -> namespace:
        data = namespace(count=0, high=0, critical=0, medium=0, low=0)
        if member:
            base = (base or model.objects).filter(
                models.Q(scan__initiator=member) | models.Q(scan__project__owner=member) 
                | models.Q(scan__project__team__users__pk=member.pk) 
                | models.Q(scan__project__visibility=Visibility.PUBLIC, scan__project__team=None))

        if project:
            base = (base or model.objects).filter(scan__project=project)

        if scan:
            base = (base or model.objects).filter(scan=scan)

        if team:
            base = (base or model.objects).filter(scan__project__team=team)

        if not base:
            return data

        data.count = len(base)
        data.critical = len(base.filter(severity=Severity.CRITICAL))
        data.high = len(base.filter(severity=Severity.HIGH))
        data.medium = len(base.filter(severity=Severity.MEDIUM))
        data.low = len(base.filter(severity=Severity.LOW))

        data.other = data.count - (data.critical + data.high
            + data.medium + data.low)
        data.rel_count = data.count if data.count > 0 else 1
        return data


# Finding implementation
class Finding(AbstractBaseFinding):
    is_custom = models.BooleanField(default=False)

    @staticmethod
    def make_uuid(*args) -> str:
        return f"SF-{uuid.uuid4()}-{uuid.uuid4()}"


class Vulnerability(AbstractBaseFinding):
    state = models.CharField(default=State.TO_VERIFY, choices=STATE_CHOICES, max_length=256)
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

    @staticmethod
    def make_uuid(*args) -> str:
        return f"SV-{uuid.uuid4()}-{uuid.uuid4()}"

