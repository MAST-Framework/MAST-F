# Generated by Django 4.1.7 on 2023-05-02 18:54

from django.db import migrations, models
import mastf.MASTF.utils.enum


class Migration(migrations.Migration):

    dependencies = [
        ('MASTF', '0017_account_description_alter_account_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hosttemplate',
            old_name='ip_adress',
            new_name='ip_address',
        ),
        migrations.AlterField(
            model_name='team',
            name='visibility',
            field=models.CharField(choices=[('Public', 'Public'), ('Private', 'Private'), ('Internal', 'Internal')], default=mastf.MASTF.utils.enum.Visibility['PRIVATE'], max_length=256),
        ),
    ]