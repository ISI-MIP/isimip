# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-19 13:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20160415_1637'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RegisterFormField',
            new_name='FormField',
        ),
    ]
