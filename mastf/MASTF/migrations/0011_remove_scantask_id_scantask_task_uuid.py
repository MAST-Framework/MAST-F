# Generated by Django 4.1.7 on 2023-04-04 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0010_remove_file_project_scan_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scantask',
            name='id',
        ),
        migrations.AddField(
            model_name='scantask',
            name='task_uuid',
            field=models.UUIDField(default=None, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
