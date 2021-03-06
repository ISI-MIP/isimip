# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-20 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0067_auto_20170120_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseimpactmodel',
            name='short_description',
            field=models.TextField(blank=True, default='', help_text='This short description should assist other researchers in getting an understanding of your model, including the main differences between model versions used for different ISIMIP simulation rounds.', null=True, verbose_name='Short model description'),
        ),
    ]
