"""
WSGI config for MASTF project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application

from mastf.MASTF import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastf.MASTF.settings')

static = os.path.join(settings.BASE_DIR, 'static')
application = WhiteNoise(get_wsgi_application(),
                         root=static, prefix='static/')
