# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-19 04:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0096_auto_20190110_0702'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sector',
            old_name='folder_name',
            new_name='drkz_folder_name',
        ),
    ]