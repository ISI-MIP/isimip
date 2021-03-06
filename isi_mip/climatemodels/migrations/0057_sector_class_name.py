# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 13:23
from __future__ import unicode_literals

from django.db import migrations, models


SECTOR_MAPPING = {
    'Agriculture': 'Agriculture',
    'Energy': 'Energy',
    'Water (global)': 'WaterGlobal',
    'Water (regional)': 'WaterRegional',
    'Biomes': 'Biomes',
    'Forests': 'Forests',
    'Marine Ecosystems and Fisheries (global)': 'MarineEcosystemsGlobal',
    'Marine Ecosystems and Fisheries (regional)': 'MarineEcosystemsRegional',
    'Biodiversity': 'Biodiversity',
    'Health': 'Health',
    'Coastal Infrastructure': 'CoastalInfrastructure',
    'Permafrost': 'Permafrost',
    'Computable General Equilibrium Modelling': 'ComputableGeneralEquilibriumModelling',
    'Agro-Economic Modelling': 'AgroEconomicModelling',
}


def set_sectors_mapping(apps, schema_editor):
    SectorModel = apps.get_model('climatemodels', 'Sector')
    for sector in SectorModel.objects.all():
        sector.class_name = SECTOR_MAPPING.get(sector.name)
        sector.save()


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0056_remove_outputdata_sector_old'),
    ]

    operations = [
        migrations.AddField(
            model_name='sector',
            name='class_name',
            field=models.CharField(choices=[('Generic Sector', 'GenericSector'), ('Agriculture', 'Agriculture'), ('Energy', 'Energy'), ('Water (global)', 'WaterGlobal'), ('Water (regional)', 'WaterRegional'), ('Biomes', 'Biomes'), ('Forests', 'Forests'), ('Marine Ecosystems and Fisheries (global)', 'MarineEcosystemsGlobal'), ('Marine Ecosystems and Fisheries (regional)', 'MarineEcosystemsRegional'), ('Biodiversity', 'Biodiversity'), ('Health', 'Health'), ('Coastal Infrastructure', 'CoastalInfrastructure'), ('Permafrost', 'Permafrost'), ('Computable General Equilibrium Modelling', 'ComputableGeneralEquilibriumModelling'), ('Agro-Economic Modelling', 'AgroEconomicModelling')], default='GenericSector', max_length=500),
        ),
        migrations.RunPython(
            set_sectors_mapping
        ),
    ]
