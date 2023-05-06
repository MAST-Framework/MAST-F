# Generated by Django 4.1.7 on 2023-04-24 05:52

from django.db import migrations, models
import mastf.MASTF.utils.enum


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0012_host_scan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bundle',
            fields=[
                ('bundle_id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('tags', models.TextField(blank=True)),
                ('risk_level', models.CharField(choices=[('Critical', 'Critical'), ('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low'), ('Info', 'Info'), ('Secure', 'Secure'), ('None', 'None')], default=mastf.MASTF.utils.enum.Severity['NONE'], max_length=32)),
                ('projects', models.ManyToManyField(related_name='bundles', to='MASTF.project')),
            ],
        ),
    ]
