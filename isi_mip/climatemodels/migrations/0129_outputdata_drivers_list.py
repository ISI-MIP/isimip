# Generated by Django 3.2.11 on 2023-01-12 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0128_alter_outputdata_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='outputdata',
            name='drivers_list',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
