# Generated by Django 4.1.7 on 2023-04-21 08:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0005_remove_host_connections_host_country_host_ip_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('cid', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=2048)),
                ('is_exported', models.BooleanField(default=False)),
                ('is_protected', models.BooleanField(default=True)),
                ('category', models.CharField(choices=[('Activity', 'Activity'), ('Service', 'Service'), ('Receiver', 'Receiver'), ('Provider', 'Provider')], max_length=256, null=True)),
                ('scanner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MASTF.scanner')),
            ],
        ),
    ]
