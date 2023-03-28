from abc import ABCMeta
from enum import Enum
from django.db.models import Count

from mastf.MASTF.models import (
    Vulnerability, Project, ProjectScanner,
    Details, PermissionFinding
)

__scanners__ = {}

def Plugin(clazz):
    clazz()
    return clazz

class Extension(Enum):
    EXT_VULNERABILITIES = 'vulnerabilities'
    EXT_PERMISSIONS = 'permissions'
    EXT_DETAILS = 'details'

    def __str__(self) -> str:
        return self.value

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.value == __value
        return super().__eq__(__value)

    def __ne__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.value != __value
        return super().__ne__(__value)


class ScannerPlugin(metaclass=ABCMeta):

    name: str = None
    """The name of this scanner type"""

    help: str = None
    """The help that will be displayed on the WebUI"""

    title: str = None
    """Actual name (more details than ``name``)"""

    extensions: list = []

    def __init__(self) -> None:
        if not self.name:
            raise ValueError("The scanner's name can not be null!")

        if self.name in __scanners__:
            raise KeyError("Scanner already registered")

        __scanners__[self.name.lower()] = self

    def context(self, extension: str, project) -> dict:
        """Generates the rendering context for the given extension

        :param extension: the extension to render
        :type extension: str
        :return: the final context
        :rtype: dict
        """
        
        func_name = f"ext_{extension}"
        if hasattr(self, func_name):
            return getattr(self, func_name)(project)
        
        return {}

    @staticmethod
    def all() -> dict:
        return __scanners__
    
    @staticmethod
    def all_of(project: Project) -> dict:
        result = {}
        if not project:
            return result
        
        for key, value in __scanners__.items():
            if ProjectScanner.objects.filter(scanner=key, project=project).exists():
                result[key] = value
        return result

    def ext_vulnerabilities(self, project: Project) -> dict:
        context = {
            'data': [],
            'vuln_count': 0
        }

        vuln = (Vulnerability.objects.filter(scan__project=project, scanner=self.name)
                .values('language').annotate(lcount=Count('language'))
                .order_by())
        if len(vuln) == 0:
            return context

        data = context['data']
        for language in vuln:
            lang = { 'name': language['language'], 'count': language['lcount'] }
            categories = []

            vuln = ( Vulnerability.objects.filter(
                scan__project=project, scanner=self.name, language=language['language'])
                    .values('template').annotate(tcount=Count('template'))
                    .order_by()
            )
            for category in vuln:
                template = category['template'].title
                cat = {'name': template, 'count': category['tcount'], 'vuln_data': []}
                for vulnerability in Vulnerability.objects.filter(
                    scan__project=project, scanner=self.name, language=language['language'],
                    template = category['template']):
                    cat['vuln_data'].append(vulnerability)

                categories.append(cat)

            lang['categories'] = categories
            data.append(lang)

    def ext_permissions(self, project: Project) -> dict:
        data = []
        for finding in PermissionFinding.objects.filter(scan__project=project):
            data.append(finding)
            
        return {'data': data}
    
    def ext_details(self, project: Project) -> dict:
        details = Details.objects.filter(scan__project=project).first()
        data = {}
        
        if details:
            data['name'] = details.name    
            data['scan_type'] = "TODO"
            data['CVSS'] = "TODO"
        return { 'data': data }
            
