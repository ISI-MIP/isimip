# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-11-11 13:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0107_auto_20201104_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='fire',
            name='natural_ignition_implemented',
            field=models.TextField(blank=True, default='', null=True, verbose_name='How are natural ignitions implemented? Which data is used and how is it scaled?'),
        ),
    ]
