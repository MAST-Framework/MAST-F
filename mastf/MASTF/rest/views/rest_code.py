from django.shortcuts import get_object_or_404

from rest_framework import permissions, authentication, views
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from mastf.MASTF import settings
from mastf.MASTF.rest.permissions import IsOwnerOrPublic
from mastf.MASTF.models import Finding

class FindingCodeView(views.APIView):

    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        authentication.TokenAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated & IsOwnerOrPublic
    ]

    def get(self, request: Request, finding_id: str) -> Response:
        finding = get_object_or_404(Finding.objects.all(), finding_id=finding_id)

        src_file = finding.source_file
        language = finding.language
        if not src_file or not language:
            return Response({'detail': 'Invalid file pointer'}, status.HTTP_204_NO_CONTENT)

        # validate whether the requesting user has the necessary
        # permissions to view the file
        project = finding.scan.project
        self.check_object_permissions(request, project)

        # Either provide the whole file or send a code
        # snippet with all relevant lines
        path = settings.PROJECTS_ROOT / str(project.project_uuid) / "src"
        if not path.exists():
            return Response({'detail': "Project source file directory does not exist"}, 
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        path = path / language / src_file
        if not path.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # TODO: Add size check
        size = path.stat().st_size
        
        data = {
            'name': finding.source_file,
            'code': path.open().read()
        }
        return Response(data)

