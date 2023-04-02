# Generated by Django 4.1.7 on 2023-03-31 13:49

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('md5', models.CharField(default='', max_length=32, primary_key=True, serialize=False)),
                ('sha256', models.CharField(default='', max_length=64)),
                ('sha1', models.CharField(default='', max_length=40)),
                ('file_name', models.CharField(default='', max_length=256)),
                ('file_size', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FindingTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_id', models.CharField(max_length=50, null=True)),
                ('title', models.CharField(blank=True, max_length=256)),
                ('description', models.CharField(blank=True, max_length=4096)),
                ('severity', models.CharField(max_length=256, null=True)),
                ('format_keys', models.CharField(max_length=4096, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('permission_uuid', models.UUIDField(primary_key=True, serialize=False)),
                ('identifier', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256, null=True)),
                ('protection_level', models.CharField(blank=True, max_length=256)),
                ('dangerous', models.BooleanField(default=False)),
                ('group', models.CharField(max_length=256, null=True)),
                ('short_description', models.CharField(blank=True, max_length=256)),
                ('description', models.CharField(blank=True, max_length=4096)),
                ('risk', models.CharField(max_length=8192, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_uuid', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, null=True)),
                ('tags', models.CharField(max_length=4096, null=True)),
                ('visibility', models.CharField(max_length=32, null=True)),
                ('risk_level', models.CharField(max_length=16, null=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('scan_uuid', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('origin', models.CharField(max_length=32, null=True)),
                ('source', models.CharField(max_length=256, null=True)),
                ('scan_type', models.CharField(max_length=50, null=True)),
                ('start_date', models.DateField(default=datetime.datetime.now)),
                ('end_date', models.DateField(null=True)),
                ('status', models.CharField(max_length=256, null=True)),
                ('risk_level', models.CharField(max_length=256, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('finished', models.BooleanField(default=False)),
                ('initiator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.project')),
            ],
        ),
        migrations.CreateModel(
            name='Vulnerability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finding_id', models.CharField(blank=True, max_length=256)),
                ('language', models.CharField(max_length=256, null=True)),
                ('severity', models.CharField(max_length=32)),
                ('source_file', models.CharField(max_length=256, null=True)),
                ('source_line', models.CharField(max_length=256, null=True)),
                ('discovery_date', models.DateField(null=True)),
                ('scanner', models.CharField(max_length=256, null=True)),
                ('state', models.CharField(max_length=256, null=True)),
                ('status', models.CharField(max_length=256, null=True)),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.scan')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.findingtemplate')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScanResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recurring_results', models.IntegerField(default=0)),
                ('new_results', models.IntegerField(default=0)),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.scan')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectScanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scanner', models.CharField(max_length=256, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.file')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.project')),
            ],
        ),
        migrations.CreateModel(
            name='PermissionFinding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finding_id', models.CharField(blank=True, max_length=256)),
                ('language', models.CharField(max_length=256, null=True)),
                ('severity', models.CharField(max_length=32)),
                ('source_file', models.CharField(max_length=256, null=True)),
                ('source_line', models.CharField(max_length=256, null=True)),
                ('discovery_date', models.DateField(null=True)),
                ('scanner', models.CharField(max_length=256, null=True)),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.permission')),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.scan')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.findingtemplate')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Finding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finding_id', models.CharField(blank=True, max_length=256)),
                ('language', models.CharField(max_length=256, null=True)),
                ('severity', models.CharField(max_length=32)),
                ('source_file', models.CharField(max_length=256, null=True)),
                ('source_line', models.CharField(max_length=256, null=True)),
                ('discovery_date', models.DateField(null=True)),
                ('scanner', models.CharField(max_length=256, null=True)),
                ('is_custom', models.BooleanField(default=False)),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.scan')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.findingtemplate')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, null=True)),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='MASTF.scan')),
            ],
        ),
        migrations.CreateModel(
            name='AccountData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_private', models.BooleanField(default=True)),
                ('role', models.CharField(max_length=256, null=True)),
                ('avatar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MASTF.file')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
