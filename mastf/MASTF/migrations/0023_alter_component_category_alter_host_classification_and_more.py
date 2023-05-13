# Generated by Django 4.1.7 on 2023-05-08 10:56

from django.db import migrations, models
import mastf.MASTF.utils.enum


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0022_alter_package_artifact_id_alter_package_group_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='category',
            field=models.CharField(choices=[('Activity', 'Activity'), ('Service', 'Service'), ('Receiver', 'Receiver'), ('Provider', 'Provider'), ('view', 'view')], max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='classification',
            field=models.CharField(choices=[('Invalid', 'Invalid'), ('Tracker', 'Tracker'), ('Malware', 'Malware'), ('Ok', 'Ok'), ('Not Set', 'Not Set')], default=mastf.MASTF.utils.enum.HostType['NOT_SET'], max_length=256),
        ),
        migrations.AlterField(
            model_name='package',
            name='type',
            field=models.CharField(choices=[('Github', 'Github'), ('Dart', 'Dart'), ('Cordova', 'Cordova'), ('Flutter', 'Flutter'), ('Native', 'Native'), ('Maven', 'Maven'), ('None', 'None')], default=mastf.MASTF.utils.enum.PackageType['NONE'], max_length=256),
        ),
    ]