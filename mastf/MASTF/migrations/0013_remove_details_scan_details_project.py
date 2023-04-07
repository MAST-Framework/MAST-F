# Generated by Django 4.1.7 on 2023-04-04 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0012_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='details',
            name='scan',
        ),
        migrations.AddField(
            model_name='details',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='MASTF.project'),
        ),
    ]