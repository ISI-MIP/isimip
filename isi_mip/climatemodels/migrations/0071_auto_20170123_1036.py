# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-23 09:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0070_auto_20170123_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outputdata',
            name='scenarios',
            field=models.ManyToManyField(blank=True, to='climatemodels.Scenario'),
        ),
        migrations.RemoveField(
            model_name='outputdata',
            name='simulation_round',
        ),
        migrations.AddField(
            model_name='outputdata',
            name='simulation_round',
            field=models.ManyToManyField(to='climatemodels.SimulationRound'),
        ),
    ]
