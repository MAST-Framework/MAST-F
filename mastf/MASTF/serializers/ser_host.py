from rest_framework import serializers

from mastf.MASTF.models import (
    Host,
    DataCollectionGroup,
    CipherSuite,
    TLS
)

from .base import ManyToManyField, ManyToManySerializer

__all__ = [
    'DataCollectionGroupSerializer',
    'TLSSerializer',
    'CipherSuiteSerializer',
    'HostSerializer',
]

class DataCollectionGroupSerializer(ManyToManySerializer):
    rel_fields = ['hosts']
    hosts = ManyToManyField(Host)

    class Meta:
        model = DataCollectionGroup
        fields = '__all__'

class TLSSerializer(ManyToManySerializer):
    rel_fields = ['hosts']
    hosts = ManyToManyField(Host)

    class Meta:
        model = TLS
        fields = '__all__'

class CipherSuiteSerializer(ManyToManySerializer):
    rel_fields = ['hosts']
    hosts = ManyToManyField(Host)

    class Meta:
        model = CipherSuite
        fields = '__all__'

class HostSerializer(ManyToManySerializer):
    tlsversions = ManyToManyField(TLS)
    suites = ManyToManyField(CipherSuite)
    collected_data = ManyToManyField(DataCollectionGroup)

    class Meta:
        model = Host
        fields = '__all__'
