import uuid

from django.db import models
from django.contrib.auth.models import User

from mastf.MASTF.utils.enum import Platform

from .base import Project, namespace, RISK_CHOICES, Team
from .mod_scan import Scan, Scanner


PLATFORM_CHOICES = [(str(x), str(x)) for x in Platform]

class Package(models.Model):
    name = models.CharField(max_length=512, null=True)
    artifact_id = models.CharField(max_length=512, null=True)
    group_id = models.CharField(max_length=512, null=True)
    platform = models.CharField(default=Platform.UNKNOWN, choices=PLATFORM_CHOICES, max_length=256)
    