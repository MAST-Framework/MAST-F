# Generated by Django 4.1.7 on 2023-05-13 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0023_alter_component_category_alter_host_classification_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='scantask',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
