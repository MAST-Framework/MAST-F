import django
import os
import sys

from uuid import uuid4

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastf.MASTF.settings')
django.setup()

from mastf.MASTF.models import *


def setup_host():
    scan = Scan.objects.first()
    scanner = Scanner.objects.first()
    for i in range(10):
        tls = TLS(pk=uuid4(), version=f"TLS{i}.0", recommended=False)
        tls.save()

        cipher = CipherSuite(pk=uuid4(), name=f"RSA{i}.0", recommended=True)
        cipher.save()

        conn = ConnectionInfo(pk=uuid4(), ip=f'129.168.178.{i}', port=8000, protocol='HTTP', country="United States",
                              longitude=60.472024 + i, latitude=8.468946 + i)
        conn.save()
        host = Host(pk=f"host_{uuid4()}", scan=scan, classification='Tracker', domain=f'db-srv{i}.domain.com', scanner=scanner)

        host.save()
        host.tlsversions.add(tls)
        host.suites.add(cipher)
        host.connections.add(conn)
        host.save()

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