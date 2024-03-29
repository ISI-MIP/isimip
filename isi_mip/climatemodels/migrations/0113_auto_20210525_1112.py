# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2021-05-25 09:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0112_impactmodel_dataset_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='BiodiversityModelOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.RemoveField(
            model_name='biodiversity',
            name='model_output',
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='dataset_history',
            field=models.URLField(blank=True, help_text='Information about data replacements, caveats and DOIs is contained within the page of every data set listed after this link.', null=True, verbose_name='Dataset history'),
        ),
        migrations.AddField(
            model_name='biodiversity',
            name='model_output',
            field=models.ManyToManyField(blank=True, null=True, to='climatemodels.BiodiversityModelOutput', verbose_name='Model output'),
        ),
    ]
