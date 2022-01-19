# Generated by Django 3.2.11 on 2022-01-19 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0115_auto_20220119_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inputdata',
            name='data_link',
            field=models.URLField(blank=True, help_text='Link to the https://data.isimip.org/ repository.', null=True),
        ),
        migrations.AlterField(
            model_name='inputdata',
            name='doi_link',
            field=models.URLField(blank=True, help_text='Link to the https://doi.org system.', null=True),
        ),
    ]
