# This file defines default mixins that can be used within each
# extension of a scanner.
from django.db.models import Count

from mastf.MASTF.models import (
    Project,
    Details,
    Namespace,
    File,
    PermissionFinding,
    Vulnerability,
    Finding,
    ProjectScanner
)


class DetailsMixin:
    """Add-on to generate app details

    If you use this mixin and you enable chart-rendering, they will
    be displayed on the front page of scan results.
    """

    charts: bool = True
    """Defines whether summary charts should be displayed on the
    details page."""

    def ctx_details(self, project: Project, file: File, scanner: ProjectScanner) -> dict:
        """Returns the details context for the desired extension.

        :param scan: the scan to view
        :type scan: Scan
        :return: all relevant context information
        :rtype: dict
        """
        context = Namespace()
        context.details = Details.objects.filter(scan__project=project, file=file).first()
        context.charts = self.charts
        return context


class PermissionsMixin:
    """Add-on to generate permission lists according to the selected file

    The returned data will be a list of ``PermissionFinding`` instances that store
    information where the permission has been found and the actual ``AppPermission``
    reference.
    """

    def ctx_permissions(self, project: Project, file: File, scanner: ProjectScanner) -> list:
        """Returns all permissions mapped to a specific file."""
        return PermissionFinding.objects.filter(scan__project=project, scan__file=file, scanner=scanner)


class VulnerabilitiesMixin:
    """Add-on to generate vulnerabilites according to the selected file.
    """

    def ctx_vulnerabilities(self, project: Project, file: File, scanner: ProjectScanner) -> list:
        """Returns all vulnerabilities that have been identified in the scan target.

        :param project: the project instance
        :type project: Project
        :param file: the scan target
        :type file: File
        :return: a list of vulnerabilities
        :rtype: list
        """
        vuln = Vulnerability.objects.filter(scan__project=project, scan__file=file, scanner=scanner)
        data = []

        languages = vuln.values('language').annotate(lcount=Count('language')).order_by()
        if len(languages) == 0:
            return data

        for language in languages:
            lang = { 'name': language['language'], 'count': language['lcount'] }
            categories = []

            templates = (vuln.filter(language=lang['name'])
                .values('template').annotate(tcount=Count('template'))
                .order_by())

            for category in templates:
                template = category['template']
                cat = {'name': template.title if template else 'Untitled', 'count': category['tcount']}

                cat['vuln_data'] = vuln.filter(language=lang['name'], template=template)
                categories.append(cat)

            lang['categories'] = categories
            data.append(lang)
        return data



class FindingsMixins:
    """Add-on to generate a finding list according to the selected file."""

    def ctx_findings(self, project: Project, file: File, scanner: ProjectScanner) -> list:
        """Returns all findings that have been identified in the scan target.

        :param project: the project instance
        :type project: Project
        :param file: the scan target
        :type file: File
        :return: a list of vulnerabilities
        :rtype: list
        """
        return Finding.objects.filter(scan__project=project, scan__file=file, scanner=scanner)

