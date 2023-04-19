# This file defines default mixins that can be used within each
# extension of a scanner.
from django.db.models import Count

from mastf.MASTF.models import (
    Scan,
    Details,
    namespace,
    File,
    PermissionFinding,
    Vulnerability,
    Finding,
    Scanner,
    FindingTemplate,
    Host
)

from mastf.MASTF.serializers import HostSerializer


class DetailsMixin:
    """Add-on to generate app details

    If you use this mixin and you enable chart-rendering, they will
    be displayed on the front page of scan results.
    """

    charts: bool = True
    """Defines whether summary charts should be displayed on the
    details page."""

    def ctx_details(self, scan: Scan, file: File, scanner: Scanner) -> dict:
        """Returns the details context for the desired extension.

        :param scan: the scan to view
        :type scan: Scan
        :return: all relevant context information
        :rtype: dict
        """
        context = namespace()
        context.details = Details.objects.filter(scan=scan, file=file).first()
        context.charts = self.charts
        return context


class PermissionsMixin:
    """Add-on to generate permission lists according to the selected file

    The returned data will be a list of ``PermissionFinding`` instances that store
    information where the permission has been found and the actual ``AppPermission``
    reference.
    """

    def ctx_permissions(self, scan: Scan, file: File, scanner: Scanner) -> list:
        """Returns all permissions mapped to a specific file."""
        return PermissionFinding.objects.filter(scan=scan, scan__file=file, scanner=scanner)


class VulnerabilitiesMixin:
    """Add-on to generate vulnerabilites according to the selected file.
    """

    def ctx_vulnerabilities(self, scan: Scan, file: File, scanner: Scanner) -> list:
        """Returns all vulnerabilities that have been identified in the scan target.

        :param project: the project instance
        :type project: Project
        :param file: the scan target
        :type file: File
        :return: a list of vulnerabilities
        :rtype: list
        """
        vuln = Vulnerability.objects.filter(scan=scan, scanner=scanner)
        data = []

        languages = vuln.values('snippet__language').annotate(lcount=Count('snippet__language')).order_by()
        if len(languages) == 0:
            return data

        for language in languages:
            lang = { 'name': language['snippet__language'], 'count': language['lcount'] }
            categories = []

            templates = (vuln.filter(snippet__language=lang['name'])
                .values('template').annotate(tcount=Count('template'))
                .order_by())

            for category in templates:
                template_pk = category['template']
                template = FindingTemplate.objects.get(pk=template_pk)
                cat = {'name': template.title if template else 'Untitled', 'count': category['tcount']}

                cat['vuln_data'] = vuln.filter(snippet__language=lang['name'], template=template)
                categories.append(cat)

            lang['categories'] = categories
            data.append(lang)
        return data


class FindingsMixins:
    """Add-on to generate a finding list according to the selected file."""

    def ctx_findings(self, scan: Scan, file: File, scanner: Scanner) -> list:
        """Returns all findings that have been identified in the scan target.

        :param project: the project instance
        :type project: Project
        :param file: the scan target
        :type file: File
        :return: a list of vulnerabilities
        :rtype: list
        """
        data = []
        findings = Finding.objects.filter(scan=scan, scanner=scanner)

        templates = (findings.values('template')
            .annotate(tcount=Count('template'))
            .order_by())
        if len(templates) == 0:
            return data

        for category in templates:
            pk = category['template']
            template = FindingTemplate.objects.get(pk=pk)
            data.append({
                'name': template.title if template else 'Untitled',
                'count': category['tcount'],
                'finding_data': findings.filter(template=template)
            })

        return data


class HostsMixin:

    def ctx_hosts(self, scan: Scan, file: File, scanner: Scanner) -> list:
        """Returns all host that have been identified within the scan target.

        :param project: the project instance
        :type project: Project
        :param file: the scan target
        :type file: File
        :return: a list of vulnerabilities
        :rtype: list
        """
        return Host.objects.filter(scan=scan, scanner=scanner)

    def res_hosts(self, scan: Scan, scanner: Scanner) -> list:
        data = Host.objects.filter(scan=scan, scanner=scanner)
        return HostSerializer(data, many=True).data
