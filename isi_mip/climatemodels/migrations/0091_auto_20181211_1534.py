# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-11 14:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0090_auto_20181126_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='forests',
            name='data_profound_db',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Which data from PROFOUND DB did you use for initialisation (name of variable, which year)? From stand data or from individual tree data?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='harvesting_simulated',
            field=models.TextField(blank=True, default='', null=True, verbose_name='When is harvesting simulated by your model (start/middle/end of the year, i.e., before or after the growing season)?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='initial_state',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Do you provide the initial state in your simulation outputs (i.e., at year 0; before the simulation starts)?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='initialize_model',
            field=models.TextField(blank=True, default='', null=True, verbose_name='How did you initialize your model, e.g. using Individual tree dbh and height or stand basal area?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='leap_years',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Does your model consider leap-years or a 365 calendar only? Or any other calendar?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='management_implementation',
            field=models.TextField(blank=True, default='', null=True, verbose_name='How is management implemented? E.g. do you harvest biomass/basal area proportions or by tree numbers or dimensions (target dbh)?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='nitrogen_simulation',
            field=models.TextField(blank=True, default='', null=True, verbose_name='How did you simulate nitrogen deposition from 2005 onwards in the 2b picontrol run? Please confirm you kept them constant at 2005-levels?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='noco2_scenario',
            field=models.TextField(blank=True, default='', null=True, verbose_name='How are models implementing the noco2 scenario? Please confirm that co2 is follwing the historical trend (based on PROFUND DB) until 2000 (for ISIMIPFT) or 2005 (for ISIMIP2b) and then fixed at 2000 or 2005 value respectively?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='output_dbh_class',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Did you report any output per dbh-class? if yes, which variables?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='regenerate',
            field=models.TextField(blank=True, default='', null=True, verbose_name='How do you regenerate? Do you plant seedlings one year after harvest or several years of gap and then plant larger saplings?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='simulate_minor_tree',
            field=models.TextField(blank=True, default='', null=True, verbose_name='In hyytiälä and kroof, how did you simulate the "minor tree species"? e.g. in hyytiälä did you simulate only pine trees and removed the spruce trees or did you interpret spruce basal area as being pine basal area?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='soil_depth',
            field=models.TextField(blank=True, default='', null=True, verbose_name='What is the soil depth you assumed for each site and how many soil layers (including their depths) do you assume in each site? Please upload a list of the soil depth and soil layers your model assumes for each site.'),
        ),
        migrations.AddField(
            model_name='forests',
            name='total_calculation',
            field=models.TextField(blank=True, default='', null=True, verbose_name='When you report a variable as "xxx-total" does it equal the (sum of) "xxx-species" value(s)? or are there confounding factors such as ground/herbaceous vegetation contributing to the "total" in your model?'),
        ),
        migrations.AddField(
            model_name='forests',
            name='unmanaged_simulations',
            field=models.TextField(blank=True, default='', null=True, verbose_name='How are the unmanaged simulations designed? Is there some kind of regrowth/regeneration or are the existing trees just growing older and older?'),
        ),
    ]
