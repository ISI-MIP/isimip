# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-20 18:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0017_auto_20160420_1434'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coastalinfrastructure',
            options={'verbose_name': 'Coastal Infrastructure', 'verbose_name_plural': 'Coastal Infrastructure'},
        ),
        migrations.AlterModelOptions(
            name='computablegeneralequilibriummodelling',
            options={'verbose_name': 'Computable General Equilibrium Modelling', 'verbose_name_plural': 'Computable General Equilibrium Modelling'},
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='sector',
            field=models.CharField(choices=[('Agriculture', 'Agriculture'), ('Energy', 'Energy'), ('Water (global)', 'Water (global)'), ('Water (regional)', 'Water (regional)'), ('Biomes', 'Biomes'), ('Forests', 'Forests'), ('Marine Ecosystems and Fisheries (global)', 'Marine Ecosystems and Fisheries (global)'), ('Marine Ecosystems and Fisheries (regional)', 'Marine Ecosystems and Fisheries (regional)'), ('Biodiversity', 'Biodiversity'), ('Health', 'Health'), ('Coastal Infrastructure', 'Coastal Infrastructure'), ('Permafrost', 'Permafrost'), ('Computable General Equilibrium Modelling', 'Computable General Equilibrium Modelling'), ('Agro-Economic Modelling', 'Agro-Economic Modelling')], max_length=500),
        ),
        migrations.AlterField(
            model_name='outputdata',
            name='sector',
            field=models.CharField(choices=[('Agriculture', 'Agriculture'), ('Energy', 'Energy'), ('Water (global)', 'Water (global)'), ('Water (regional)', 'Water (regional)'), ('Biomes', 'Biomes'), ('Forests', 'Forests'), ('Marine Ecosystems and Fisheries (global)', 'Marine Ecosystems and Fisheries (global)'), ('Marine Ecosystems and Fisheries (regional)', 'Marine Ecosystems and Fisheries (regional)'), ('Biodiversity', 'Biodiversity'), ('Health', 'Health'), ('Coastal Infrastructure', 'Coastal Infrastructure'), ('Permafrost', 'Permafrost'), ('Computable General Equilibrium Modelling', 'Computable General Equilibrium Modelling'), ('Agro-Economic Modelling', 'Agro-Economic Modelling')], max_length=500),
        ),
    ]
