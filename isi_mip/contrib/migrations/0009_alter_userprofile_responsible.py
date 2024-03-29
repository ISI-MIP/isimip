# Generated by Django 3.2.11 on 2022-10-28 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0123_auto_20221028_1008'),
        ('contrib', '0008_rename_involved_userprofile_responsible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='responsible',
            field=models.ManyToManyField(blank=True, related_name='impact_model_responsible', to='climatemodels.ImpactModel'),
        ),
    ]
