import django
import os
import sys
import random

from uuid import uuid4

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastf.MASTF.settings')
django.setup()

from mastf.MASTF.models import *
from mastf.MASTF.utils.enum import HostType, DataProtectionLevel

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

def setup_host_data():
    for i in range(5):
        TLS(pk=uuid4(), version=f"TLS{i}.0", recommended=i>3).save()

    for i in range(5):
        CipherSuite(pk=uuid4(), name=f"RSA{i}.0", recommended=i>3).save()

    DataCollectionGroup(pk=uuid4(), group="Authentication",
                        protection_level=DataProtectionLevel.PRIVATE).save()

def setup_hosts():
    s = Scan.objects.first()
    sn = Scanner.objects.first()

    for i in range(5):
        htype = random.choice(list(HostType))
        domain = f"db{i}-srv.domain.com"
        protocol = "HTTPS"
        longitude = 5.6 + i
        latitude = 20.5 + i

        host = Host(pk=f"hst_{uuid4()}", scan=s, scanner=sn, classification=htype,
                    protocol=protocol, longitude=longitude,
                    latitude=latitude)

        host.save()
        host.tlsversions.add(TLS.objects.first())
        host.suites.add(CipherSuite.objects.first())
        host.collected_data.add(DataCollectionGroup.objects.first())
        host.save()

def setup_package():
    for i in range(10):
        Package(pk=uuid4(), name=f"Package{i}", artifact_id=f"example-{i}",
                group_id=f"com.example.dev{i}", type="None", platform="Android").save()

if __name__ == '__main__':
    mod = sys.modules[__name__]
    func = getattr(mod, sys.argv[1])
    func()