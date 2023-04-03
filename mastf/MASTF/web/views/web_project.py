from django.db.models import QuerySet, Q

from celery.result import AsyncResult

from mastf.MASTF.mixins import (
    ContextMixinBase, 
    UserProjectMixin, 
    VulnContextMixin
)
from mastf.MASTF.models import (
    Vulnerability, 
    Scan, 
    ScanTask, 
    Finding, 
    Namespace,
)
from mastf.MASTF.serializers import CeleryResultSerializer
from mastf.MASTF.scanners.plugin import ScannerPlugin


__all__ = [
    'UserProjectDetailsView', 'UserProjectScanHistoryView',
    'UserProjectScannersView'
]

OVERVIEW_PATH = 'project/project-overview.html'

class UserProjectDetailsView(UserProjectMixin, ContextMixinBase):
    template_name = OVERVIEW_PATH

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.apply_project_context(context, self.kwargs['project_uuid'])

        project = context['project']
        context['active'] = 'tabs-overview'

        vuln = Vulnerability.objects.filter(scan__project=project)
        context['risk_count'] = len(vuln)
        context['verified'] = len(vuln.filter())
        context['scan'] = Scan.last_scan(project)

        tasks = ScanTask.active_tasks(project=project)
        context['is_active'] = len(tasks) > 0
        if context['is_active']:
            active_data = []
            for task in tasks:
                result = AsyncResult(task.celery_id)
                active_data.append(CeleryResultSerializer(result).data)
            context['active_data'] = active_data
            
        return context


class UserProjectScanHistoryView(UserProjectMixin, ContextMixinBase):
    template_name = OVERVIEW_PATH
    
    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        self.apply_project_context(context, self.kwargs['project_uuid'])
        
        project = context['project']
        context['active'] = 'tabs-scan-history'
        context['scan_data'] = [ 
            self.get_scan_history(scan) for scan in Scan.objects.filter(project=project)
        ]
        return context
    
    def get_scan_history(self, scan: Scan) -> dict:
        data = Namespace()
        vuln_data = Vulnerability.stats(scan=scan)
        finding_data = Finding.stats(scan=scan)
        
        data.scan = scan
        data.high_risks = vuln_data.high_vuln + finding_data.high_finding
        data.medium_risks = vuln_data.medium_vuln + finding_data.medium_finding
        data.low_risks = vuln_data.low_vuln + finding_data.low_finding
        return data


class UserProjectScannersView(UserProjectMixin, VulnContextMixin, ContextMixinBase):
    template_name = OVERVIEW_PATH
    
    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        self.apply_project_context(context, self.kwargs['project_uuid'])
        context['active'] = 'tabs-scanners'
        
        project = context['project']
        scans = Scan.objects.filter(project=project).order_by("start_date")
        scanners = ScannerPlugin.all_of(project)
        
        results = {}
        for name, scanner in scanners:
            results[scanner.name] = self.get_scan_results(scans, name)
        
        return context
    
    def get_scan_results(self, scans: QuerySet, name: str) -> dict:
        data = Namespace()
        data.vuln_count = 0
        data.vuln_data = []
        data.start_date = None
        data.results = 0
        
        if len(scans) == 0:
            return data
        
        data.start_date = str(scans[0].start_date)
        scan_query = Q(scan=scans[0])
        for scan in scans[ 1: ]:
            scan_query = scan_query | Q(scan=scan)
        
        vuln = Vulnerability.objects.filter(Q(scanner=name), scan_query)
        self.apply_vuln_context(data, vuln)
        data.results = len(vuln)
        return data
                    
        
    
