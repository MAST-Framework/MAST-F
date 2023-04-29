from rest_framework import permissions, authentication, status
from rest_framework.response import Response

from django.db.models.functions import ExtractMonth
from django.db.models import Count

from mastf.MASTF.serializers import BundleSerializer
from mastf.MASTF.models import Bundle, Scanner, Vulnerability, Project
from mastf.MASTF.forms import BundleForm
from mastf.MASTF.utils.enum import Severity
from mastf.MASTF.permissions import (
    CanEditBundle,
    CanDeleteBundle,
    CanViewBundle
)

from .base import (
    CreationAPIViewBase,
    APIViewBase,
    ListAPIViewBase,
    APIView,
    GetObjectMixin
)

__all__ = [
    'BundleView',
    'BundleCreationView',
    'BundleListView',
    'BundleChartView',
    'BundleProjectDeletionView'
]

class BundleView(APIViewBase):
    model = Bundle
    serializer_class = BundleSerializer
    permission_classes = [permissions.IsAuthenticated & (
        CanDeleteBundle | CanEditBundle
    )]

class BundleCreationView(CreationAPIViewBase):
    model = Bundle
    form_class = BundleForm
    permission_classes = [permissions.IsAuthenticated]

    def set_defaults(self, request, data: dict) -> None:
        data['owner'] = request.user

class BundleListView(ListAPIViewBase):
    queryset = Bundle.objects.all()
    serializer_class = BundleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def filter_queryset(self, queryset):
        return Bundle.get_by_owner(self.request.user, queryset)

class BundleProjectDeletionView(GetObjectMixin, APIView):
    model = Bundle
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        authentication.TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated & CanEditBundle
    ]

    def delete(self, request, *args, **kwargs) -> Response:
        bundle: Bundle = self.get_object()
        project = self.get_object(Project, 'project_uuid', check=False)

        bundle.projects.remove(project)
        return Response({'success': True})


class BundleChartView(GetObjectMixin, APIView):
    model = Bundle
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        authentication.TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated & CanViewBundle
    ]

    def get(self, request, pk, name: str) -> Response:
        func_name = f"chart_{name.replace('-', '_')}"

        data = {}
        if hasattr(self, func_name):
            data = getattr(self, func_name)(self.get_object())
            if not data.get('success', False):
                return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data)

    def get_findings(self, bundle: Bundle):
        pks = [x.pk for x in bundle.projects.all()]
        return Vulnerability.objects.filter(scan__project__pk__in=pks)


    def chart_aging_report(self, bundle: Bundle) -> dict:
        findings = self.get_findings(bundle)

        filtered = (
            findings.annotate(month=ExtractMonth('discovery_date'))
            .values('month', 'severity')
            .annotate(count=Count('pk'))
            .order_by('month', 'severity')
        )

        categories = sorted(set(x['month'] for x in filtered))
        series = []
        for severity in [Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            series_data = [0] * len(categories)
            for item in filtered:
                if item['severity'] == severity:
                    idx = categories.index(item['month'])
                    series_data[idx] = item['count']

            series.append({
                'name': str(severity),
                'data': series_data
            })

        # Gets all month names
        month_names = [
             m.strftime("%B") for m in sorted(
                 set(item.discovery_date.replace(day=1) for item in Vulnerability.objects.all())
            )
        ]
        chart_data = {'series': series, 'categories': month_names, 'success': True}
        return chart_data

    def chart_results(self, bundle: Bundle) -> dict:
        name = self.request.GET.get('name', None)
        if not name:
            return {}

        fname = f"res_{name.replace('-', '_')}"
        if not hasattr(self, fname):
            return {}

        return getattr(self, fname)(bundle)

    def res_scanner_type(self, bundle: Bundle) -> dict:
        findings = self.get_findings(bundle)
        filtered = findings.values("scanner").annotate(count=Count("scanner")).order_by("scanner")

        max_count = len(findings)
        series = [0] * len(filtered)
        categories = []
        for i, element in enumerate(filtered):
            series[i] = (element['count'] // max_count) * 100
            scanner = Scanner.objects.get(pk=element['scanner'])
            categories.append(scanner.name.capitalize())

        return {
            'series': series,
            'categories': categories,
            'success': True
        }

    def res_state(self, bundle: Bundle) -> dict:
        findings = self.get_findings(bundle)
        filtered = findings.values("state").annotate(count=Count("state")).order_by("state")

        max_count = len(findings)
        series = [0] * len(filtered)
        categories = []
        for i, element in enumerate(filtered):
            series[i] = (element['count'] // max_count) * 100
            categories.append(str(element['state']).capitalize())

        return {
            'series': series,
            'categories': categories,
            'success': True
        }