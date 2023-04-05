# This file defines default mixins that can be used within each 
# extension of a scanner.
from django.shortcuts import get_object_or_404

from mastf.MASTF.models import Project, Details, Namespace

class DetailsMixin:
    """Add-on to generate app details
    
    If you use this mixin and you enable chart-rendering, they will 
    be displayed on the front page of scan results.
    """
    
    charts: bool = True
    """Defines whether summary charts should be displayed on the
    details page."""
    
    def ctx_details(self, project: Project) -> dict:
        """Returns the details context for the desired extension.

        :param scan: the scan to view
        :type scan: Scan
        :return: all relevant context information
        :rtype: dict
        """
        context = Namespace()
        context.details_data = Details.objects.filter(scan__project=project) or []
        context.charts = self.charts
        return context
        
    
    