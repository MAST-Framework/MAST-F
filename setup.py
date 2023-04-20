import django
import os
import sys

from uuid import uuid4

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastf.MASTF.settings')
django.setup()

from mastf.MASTF.models import *


def setup_vuln():
    s = Scan.objects.first()
    sn = Scanner.objects.first()

    ft = FindingTemplate(template_id=f"FT-{uuid4()}-{uuid4()}", title="Stored XSS", description="Short description...", article="android/logging")
    ft.save()
    v = Vulnerability(finding_id=f"SV-{uuid4()}-{uuid4()}", scan=s, scanner=sn, template=ft, severity='High', state='To Verify', status='New')
    st = Snippet(lines="12,143", language="java", file_name="AndroidManifest.xml", file_size="23610")
    st.save()
    v.snippet = st
    v.save()

def setup_finding():
    s = Scan.objects.first()
    sn = Scanner.objects.first()
    ft = FindingTemplate.objects.first()
    st = Snippet.objects.first()

    f = Finding(finding_id=f"SF-{uuid4()}-{uuid4()}", scan=s, scanner=sn, template=ft, severity='Low', snippet=st)
    perm = AppPermission(permission_uuid=uuid4(), identifier='android.permission.INTERNET', name='Internet', protection_level='normal', group='wlan', description='Long Description...')
    perm.save()
    scan = Scan.objects.first()
    pf = PermissionFinding(pk=f"permission_{uuid4()}", scan=scan, severity='INFO', scanner=Scanner.objects.first(), permission=perm)
    pf.save()

    f.save()

if __name__ == '__main__':
    mod = sys.modules[__name__]
    func = getattr(mod, sys.argv[1])
    func()