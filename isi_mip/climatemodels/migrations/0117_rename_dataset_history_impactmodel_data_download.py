# Generated by Django 3.2.11 on 2022-01-31 09:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0116_auto_20220119_1450'),
    ]

    operations = [
        migrations.RenameField(
            model_name='impactmodel',
            old_name='dataset_history',
            new_name='data_download',
        ),
    ]
