# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-30 12:53
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20160330_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='teaser',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, null=True),
        ),
    ]