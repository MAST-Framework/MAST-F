# Generated by Django 4.1.7 on 2023-04-18 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0003_rename_langitude_connectioninfo_latitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='scanner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='MASTF.scanner'),
        ),
    ]
