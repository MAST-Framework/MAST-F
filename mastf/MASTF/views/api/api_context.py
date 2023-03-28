from datetime import datetime

from django.db.models import Q

from mastf.MASTF import settings
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.models import (
    Project, Vulnerability, AccountData, Scan,
    Finding, ScanResult
)
from mastf.MASTF.utils.level import RiskLevel

def api_get_context(user, defaults: dict = None) -> dict:
    context = {
        'debug': settings.DEBUG_HTML,
    }

    if defaults:
        for key, value in defaults.items():
            context[key] = value

    data = AccountData.objects.filter(user=user)
    if data.exists():
        context['user_role'] = data.first().role

    return context

def __vuln_data(vuln) -> dict:
    vuln_count = len(vuln)
    critical_vuln = vuln.filter(severity=RiskLevel.CRITICAL)
    high_vuln = vuln.filter(severity=RiskLevel.HIGH)
    medium_vuln = vuln.filter(severity=RiskLevel.MEDIUM)
    low_vuln = vuln.filter(severity=RiskLevel.LOW)

    other_vuln_count = vuln_count - (len(high_vuln) + len(medium_vuln) + len(low_vuln))
    # The relative vulnerability count is used rather than the actual
    # value, because division by zero would throw errors and the page
    # wouldn't be displayed correctly.
    relative_vuln_count = vuln_count if vuln_count > 0 else 1
    return {
        'vuln_count': vuln_count,
        'vuln_data': [
            # There are only CRITICAL, HIGH, MEDIUM, LOW and SECURE entries
            {
                "name": str(RiskLevel.CRITICAL),
                "color": "bg-pink",
                "percent": len(critical_vuln) / relative_vuln_count,
                "count": len(critical_vuln)
            },
            {
                "name": str(RiskLevel.HIGH),
                "color": "bg-red",
                "percent": len(high_vuln) / relative_vuln_count,
                "count": len(high_vuln)
            },
            {
                "name": str(RiskLevel.MEDIUM),
                "color": "bg-orange",
                "percent": len(medium_vuln) / relative_vuln_count,
                "count": len(medium_vuln)
            },
            {
                "name": str(RiskLevel.LOW),
                "color": "bg-yellow",
                "percent": len(low_vuln) / relative_vuln_count,
                "count": len(low_vuln)
            },
            {
                "name": "Other",
                "color": "bg-secondary",
                "percent": other_vuln_count / relative_vuln_count,
                "count": other_vuln_count
            }
        ]
    }

def api_get_project_context(user) -> dict:
    context = api_get_context(user, {
        # Select the 'Projects'-tab when loading the page
        'active': 'tabs-projects',
        'project_count': len(Project.objects.filter(owner=user)),

        # Specifies the amount of high or medium risk projects.
        # Note: zero will be displayed as 'None'
        'risk_high': len(Project.objects.filter(owner=user, risk_level=RiskLevel.HIGH)),
        'risk_medium': len(Project.objects.filter(owner=user, risk_level=RiskLevel.MEDIUM)),

        'columns': settings.PROJECTS_TABLE_COLUMNS,
        'project_table_data': [
            # This list stores all rows with their mapped values. Note
            # that all values are mapped to their column name. Some values
            # might be special as they must contain additional information
            # such as the background color.
        ]
    })
    context.update(__vuln_data(Vulnerability.objects.filter(scan__initiator=user)))

    return context


def api_get_application_context(user) -> dict:
    context = api_get_context(user, {
         # Select the 'Applications'-tab when loading the page
        'active': 'tabs-applications',

        # The application count should be retrieved by requesting
        # all objects of the 'Application' model
        'app_count': 5,

        # Specifies the amount of high or medium risk applications
        'risk_high': 5,
        'risk_medium': 0, # zero will be displayed as 'None'

        # Data that should be transformed into several progress bars
        'risk_level_count': 5,
        'risk_level_data': [
            # There are only HIGH, MEDIUM, LOW and SECURE entries
            {
                "name": 'High',
                "color": "bg-red",
                "percent": 100,
                "count": 5
            }
        ],

        'columns': settings.APPS_TABLE_COLUMNS,
        'app_table_data': []
    })

    return context


def api_get_project_details_context(user, project_id: str, active_tab: str = "tabs-overview"):
    project = Project.objects.filter(project_uuid=project_id).first()
    return api_get_context(user, {
        'active': active_tab,
        'project': project,
        'scanners': ScannerPlugin.all(),
        'date_value': datetime.now()
    })

def api_get_project_overview_context(user, project_id: str) -> dict:
    return api_get_project_details_context(user, project_id)

def __scan_history_context(scan: Scan):
    vuln = Vulnerability.objects.filter(scan=scan)
    finding = Finding.objects.filter(Scan=scan)

    return {
        'scan_uuid': scan.scan_uuid,
        'origin': scan.origin,
        'scan_type': scan.scan_type,
        'high_risks': len(vuln.filter(severity=RiskLevel.HIGH)) + len(finding.filter(severity=RiskLevel.HIGH)),
        'medium_risks': len(vuln.filter(severity=RiskLevel.MEDIUM)) + len(finding.filter(severity=RiskLevel.MEDIUM)),
        'low_risks': len(vuln.filter(severity=RiskLevel.LOW)) + len(finding.filter(severity=RiskLevel.LOW)),
        'risk_level': scan.risk_level,
        'start_date': scan.start_date,
        'status': scan.status
    }

def api_get_project_scan_history_context(user, project_id: str) -> dict:
    context = api_get_project_details_context(user, project_id, 'tabs-scan-history')

    project = context['project']
    if not project:
        context['scan_data'] = []
    else:
        context['scan_data'] = [
            __scan_history_context(scan) for scan in Scan.objects.filter(project=project)
        ]

    return context


def __scan_results(scans: list, name: str) -> dict:
    results = {
        'vuln_count': 0,
        'vuln_data': [],
        'start_date': "",
        'results': 0
    }
    if len(scans) == 0:
        return results

    results['start_date'] = str(scans[0].start_date)

    scan_query = Q(scan=scans[0])
    for scan in scans[1:]:
        scan_query = scan_query | Q(scan=scan)

    all_vuln = Vulnerability.objects.get( Q(scanner=name), scan_query )
    results.update(__vuln_data(all_vuln))
    results['results'] = len(all_vuln)
    return results



def api_get_project_scan_data_context(user, project_id: str) -> dict:
    """Collects information of all scans with their results"""
    context = api_get_project_details_context(user, project_id, 'tabs-scanners')
    project = context['project']
    if not project:
        context['scan_results'] = []
        return context

    scan_results = {}
    scans = Scan.objects.filter(project=project).order_by("start_date")

    scanners = ScannerPlugin.all_of(project)
    for name, scanner in scanners.items():
        scan_results[scanner.name] = __scan_results(scans, name)

    context['scan_results'] = scan_results
    return context
