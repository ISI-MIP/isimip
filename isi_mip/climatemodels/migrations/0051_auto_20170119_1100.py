# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 10:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0050_auto_20170119_1059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inputdata',
            name='old_scenario',
        ),
        migrations.RemoveField(
            model_name='inputdata',
            name='old_simulation_round',
        ),
    ]
