import django
import os
from uuid import uuid4

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastf.MASTF.settings')
    django.setup()

    from mastf.MASTF.models import *

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