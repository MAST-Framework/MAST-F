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
import uuid
import re

from django.db import models
from django.contrib.auth.models import User

from mastf.MASTF.utils.enum import Severity, State, Visibility

from .base import Project, namespace, Team, Bundle
from .mod_scan import Scan, Scanner

__all__ = [
    "FindingTemplate",
    "Snippet",
    "AbstractBaseFinding",
    "Finding",
    "Vulnerability",
]

class FindingTemplate(models.Model):
    """
    Represents a model for storing information about a finding template. This model
    is used to create, update and delete templates which then are used to generate
    findings or vulnerabilities. Each template is assigned a unique ID and an
    internal ID that is used as a key for finding the template in the database.

    Examples:
    ~~~~~~~~~

    Creating a new finding template:

    >>> template = FindingTemplate(
            template_id="1",
            internal_id="template-1",
            title="Example Template",
            description="This is an example template.",
            default_severity=Severity.HIGH,
            risk="High",
            mitigation="Apply the recommended security patches.",
            article="https://example.com/article"
        )
    >>> template.save()

    Updating an existing finding template:

    >>> template = FindingTemplate.objects.get(internal_id="template-1")
    >>> template.title = "Updated Example Template"
    >>> template.description = "This is an updated example template."
    >>> template.save()

    Or deleting an existing finding template:

    >>> template = FindingTemplate.objects.get(internal_id="template-1")
    >>> template.delete()
    """

    template_id = models.CharField(max_length=128, null=True, unique=True)
    """A unique ID assigned to the template."""

    internal_id = models.CharField(max_length=256, null=True, unique=True)
    """
    A unique internal ID assigned to the template used as a key for finding the
    template in the database.
    """

    title = models.CharField(max_length=256, blank=True)
    """The title of the template."""

    description = models.TextField()
    """A description of the template."""

    default_severity = models.CharField(
        default=Severity.NONE, choices=Severity.choices, max_length=256
    )
    """
    The default severity assigned to the finding. See :class:`Severity` for more
    information.
    """

    risk = models.TextField()
    """A description of the risk associated with the finding."""

    mitigation = models.TextField()
    """A description of the mitigation steps that can be taken to resolve the finding."""

    article = models.CharField(max_length=256, null=True)
    """A link to an article associated with the finding."""

    @staticmethod
    def make_uuid(*args) -> str:
        """Used to generate a unique ID for the template.

        :return: Returns a unique UUID string in the format ``FT-{uuid4()}-{uuid4()}``.
        :rtype: str
        """
        return f"FT-{uuid.uuid4()}-{uuid.uuid4()}"

    @staticmethod
    def make_internal_id(title: str) -> str:
        """Generate an internal ID for the template based on its title.

        Returns a string in the format ``<title>`` with spaces, colons, and underscores
        replaced with hyphens and consecutive hyphens removed. The resulting string is
        then converted to lowercase. This method is used to

        :param title: the template's title
        :type title: str
        :return: the internal id
        :rtype: str
        """
        return re.sub(r"[\s_:]", "-", title).replace("--", "-").lower()


class Snippet(models.Model):
    """Django model for storing code snippets with optional information."""

    lines = models.CharField(max_length=2048, blank=True)
    """Stores lines that should be highlighted."""

    sys_path = models.CharField(max_length=1024, null=True)
    """Stores the path to the file where the snippet was found (optional, internal)."""

    language = models.CharField(max_length=32, null=True)
    """Specifies the programming language this finding was found in (optional)"""

    file_name = models.CharField(max_length=512, null=True)
    """Stores the name of the file where the snippet was found (optional)."""

    file_size = models.CharField(max_length=256, null=True)
    """Stores the size of the file where the snippet was found (optional)."""


class AbstractBaseFinding(models.Model):
    """
    AbstractBaseFinding is an abstract model that serves as a base class for all
    findings in the vulnerability scanner.
    """

    finding_id = models.CharField(max_length=256, null=False, primary_key=True)
    """A unique identifier for the finding"""

    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, null=True)
    """A foreign key that links the finding to a specific scan."""

    snippet = models.ForeignKey(Snippet, on_delete=models.SET_NULL, null=True)
    """A foreign key that links the finding to a specific code snippet"""

    severity = models.CharField(
        default=Severity.NONE, choices=Severity.choices, max_length=256
    )
    """The severity of the finding"""

    discovery_date = models.DateField(null=True, auto_now=True, auto_now_add=False)
    """Stores the date this vulnerability or finding was detected."""

    scanner = models.ForeignKey(Scanner, on_delete=models.CASCADE, null=True)
    """The scanner that found the vulnerability or finding"""

    template = models.ForeignKey(FindingTemplate, on_delete=models.CASCADE, null=True)
    """The finding template used to create the finding"""

    class Meta:
        abstract = True

    @staticmethod
    def stats(
        model,
        member: User = None,
        project: Project = None,
        scan: Scan = None,
        team: Team = None,
        base=None,
        bundle: Bundle = None,
    ) -> namespace:
        """
        This static method returns a namespace with statistics about the number of
        findings of a specific model and severity for a specific member, project,
        scan, team, base or bundle.

        :param model: the model to get the statistics for (either Vulnerability or Finding)
        :type model: :class:`django.db.models.Model`
        :param member: the member to filter the statistics for (defaults to None).
        :type member: :class:`User`, optional
        :param project: the project to filter the statistics for (defaults to None).
        :type project: :class:`Project`, optional
        :param scan: the scan to filter the statistics for (defaults to None).
        :type scan: :class:`Scan`, optional
        :param team: the team to filter the statistics for (defaults to None).
        :type team: :class:`Team`, optional
        :param base: the base queryset to filter the statistics for (defaults to None).
        :type base: :class:`django.db.models.QuerySet`, optional
        :param bundle: the bundle to filter the statistics for (defaults to None).
        :type bundle: :class:`Bundle`, optional
        :return: a namespace containing the count, high, critical, medium, low, and other
                 statistics for the given parameters.
        :rtype: :class:`namespace`

        The method works by filtering the given model based on the parameters passed and
        then returning a namespace containing the statistics of the filtered query set. If
        no parameter is passed, the method returns an empty namespace.

        The statistics returned are:

        * ``count`` - the total number of findings
        * ``high`` - the number of findings with severity HIGH
        * ``critical`` - the number of findings with severity CRITICAL
        * ``medium`` - the number of findings with severity MEDIUM
        * ``low`` - the number of findings with severity LOW
        * ``other`` - the number of findings that do not belong to any of the severity levels mentioned above
        * ``rel_count`` - the relative count, which is the count if count is greater than 0, and 1 otherwise.

        Usage example:

        To get the count of findings of the `AbstractBaseFinding` model for a specific project,
        you could use the following code:

        .. code-block:: python

            project = Project.objects.get(pk=1)
            count = AbstractBaseFinding.stats(model=Finding, project=project)
        """
        data = namespace(count=0, high=0, critical=0, medium=0, low=0)
        if member:
            base = (base or model.objects).filter(
                models.Q(scan__initiator=member)
                | models.Q(scan__project__owner=member)
                | models.Q(scan__project__team__users__pk=member.pk)
                | models.Q(
                    scan__project__visibility=Visibility.PUBLIC,
                    scan__project__team=None,
                )
            )

        if project:
            base = (base or model.objects).filter(scan__project=project)
        if scan:
            base = (base or model.objects).filter(scan=scan)
        if team:
            base = (base or model.objects).filter(scan__project__team=team)
        if bundle:
            pks = [x.pk for x in bundle.projects.all()]
            base = (base or model.objects).filter(scan__project__pk__in=pks)

        if not base:
            return data

        data.count = len(base)
        data.critical = len(base.filter(severity=Severity.CRITICAL))
        data.high = len(base.filter(severity=Severity.HIGH))
        data.medium = len(base.filter(severity=Severity.MEDIUM))
        data.low = len(base.filter(severity=Severity.LOW))

        data.other = data.count - (data.critical + data.high + data.medium + data.low)
        data.rel_count = data.count if data.count > 0 else 1
        return data


# Finding implementation
class Finding(AbstractBaseFinding):
    """A model that represents a finding.

    Inherits from AbstractBaseFinding model and adds some additional attributes.
    """

    is_custom = models.BooleanField(default=False)
    """A boolean indicating if the finding is custom or not."""

    custom_text = models.TextField(null=True, blank=True)
    """Stores custom text for a finding."""

    @staticmethod
    def make_uuid(*args) -> str:
        """A static method that generates a unique ID for a finding.

        :return:  A string representing the unique ID.
        :rtype: str
        """
        return f"SF-{uuid.uuid4()}-{uuid.uuid4()}"


class Vulnerability(AbstractBaseFinding):
    """A model that represents a vulnerability.

    Inherits from AbstractBaseFinding model and adds some additional attributes.
    """

    state = models.CharField(
        default=State.TO_VERIFY, choices=State.choices, max_length=256
    )
    """
    Stores the state of a vulnerability. See :class:`State` for information
    about the current state of a vulnerability.
    """

    status = models.CharField(null=True, max_length=256)
    """The status of this vulnerability"""

    @staticmethod
    def make_uuid(*args) -> str:
        """A static method that generates a unique ID for a vulnerability.

        :returns: A string representing the unique ID.
        :rtype: str
        """
        return f"SV-{uuid.uuid4()}-{uuid.uuid4()}"
