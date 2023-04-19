# Generated by Django 4.1.7 on 2023-04-18 10:48

from django.db import migrations, models
import django.db.models.deletion
import mastf.MASTF.utils.enum


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CipherSuite',
            fields=[
                ('cipher_uuid', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=256)),
                ('recommended', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ConnectionInfo',
            fields=[
                ('ci_uuid', models.UUIDField(primary_key=True, serialize=False)),
                ('ip', models.CharField(max_length=32, null=True)),
                ('port', models.IntegerField(default=0)),
                ('protocol', models.CharField(max_length=256, null=True)),
                ('country', models.CharField(max_length=256, null=True)),
                ('longitude', models.FloatField(null=True)),
                ('langitude', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataCollectionGroup',
            fields=[
                ('dc_uuid', models.UUIDField(primary_key=True, serialize=False)),
                ('group', models.CharField(max_length=256)),
                ('protection_level', models.CharField(choices=[('Private', 'Private'), ('Public', 'Public')], default=mastf.MASTF.utils.enum.DataProtectionLevel['PUBLIC'], max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='TLS',
            fields=[
                ('tls_uuid', models.UUIDField(primary_key=True, serialize=False)),
                ('version', models.CharField(max_length=256, null=True)),
                ('recommended', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='package',
            name='type',
            field=models.CharField(choices=[('Github', 'Github'), ('Dart', 'Dart'), ('Cordova', 'Cordova'), ('Flutter', 'Flutter'), ('Native', 'Native'), ('None', 'None')], default=mastf.MASTF.utils.enum.PackageType['NONE'], max_length=256),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('host_id', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('classification', models.CharField(choices=[('Invalid', 'Invalid'), ('Tracker', 'Tracker'), ('Ok', 'Ok'), ('Not Set', 'Not Set')], default=mastf.MASTF.utils.enum.HostType['NOT_SET'], max_length=256)),
                ('url', models.URLField(max_length=2048, null=True)),
                ('domain', models.CharField(max_length=2048, null=True)),
                ('collected_data', models.ManyToManyField(related_name='hosts', to='MASTF.datacollectiongroup')),
                ('connections', models.ManyToManyField(related_name='hosts', to='MASTF.connectioninfo')),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MASTF.scan')),
                ('snippet', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='MASTF.snippet')),
                ('suites', models.ManyToManyField(related_name='hosts', to='MASTF.ciphersuite')),
                ('tlsversions', models.ManyToManyField(related_name='hosts', to='MASTF.tls')),
            ],
        ),
    ]