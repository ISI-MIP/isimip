import json
import logging
import re
import urllib.request
from datetime import date

from django.apps import apps
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.db.models.fields import BooleanField, CharField, TextField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from wagtail.rich_text import RichText

from isi_mip.choiceorotherfield.models import ChoiceOrOtherField
from isi_mip.climatemodels.impact_model_blocks import (
    IMPACT_MODEL_QUESTION_BLOCKS, ModelSingleChoiceFieldBlock)
from isi_mip.climatemodels.management.commands._model_field_definitions import \
    MODEL_FIELD_DEFINITION
from isi_mip.climatemodels.models import (
    Agriculture, AgroEconomicModelling, Biodiversity, Biomes, BiomesForests,
    CoastalInfrastructure, ComputableGeneralEquilibriumModelling, Energy, Fire,
    Forests, Health, ImpactModel, ImpactModelQuestion, InputDataInformation,
    MarineEcosystemsGlobal, MarineEcosystemsRegional, OtherInformation,
    Permafrost, Sector, SectorInformationGroup, TechnicalInformation,
    WaterGlobal, WaterRegional)
from isi_mip.pages.models import HomePage

logger = logging.getLogger(__name__)

MODEL_LIST = (
    ('technical_information', TechnicalInformation),
    ('input_data_information', InputDataInformation),
    ('other_information', OtherInformation),
    ('agriculture', Agriculture),
    ('biomes', Biomes),
    ('fire', Fire),
    ('forests', Forests),
    ('energy', Energy),
    ('marine-ecosystems-and-fisheries-global', MarineEcosystemsGlobal),
    ('marine-ecosystems-and-fisheries-regional', MarineEcosystemsRegional),
    ('lakes-global', WaterGlobal),
    ('lakes-local', WaterRegional),
    ('biodiversity', Biodiversity),
    ('air-quality', Health),
    ('coastal-systems', CoastalInfrastructure),
    ('permafrost', Permafrost),
    ('computable-general-equilibrium-modelling', ComputableGeneralEquilibriumModelling),
    ('agro-economic-modelling', AgroEconomicModelling),
)

IGNORE_FIELD_NAME_LIST = (
    'impact_model',
    'data',
    'id',
)

# {"other_data_sets":["15"],"climate_variables":[],"land_use_data_sets":["22"],"emissions_data_sets":[],"climate_variables_info":"","socio_economic_data_sets":["81","54"],"additional_input_data_sets":"","other_human_influences_data_sets":["24"],"observed_atmospheric_climate_data_sets":["27"],"simulated_atmospheric_climate_data_sets":["59","53"]}


class Command(BaseCommand):
    help = 'Migrates the model documentation to the new dynamic and flexible format'

    def generate_json_value(self, model, fields):
        json_value = {}
        for field in fields:
            if field.name in IGNORE_FIELD_NAME_LIST:
                continue
            if field.__class__ == ForeignKey:
                field_value = getattr(model, field.name)
                field_value = field_value and field_value.pk
            elif field.__class__ == ManyToManyField:
                field_value = list(getattr(model, field.name).values_list('pk', flat=True))
            else:
                field_value = getattr(model, field.name)
            json_value.update({
                field.name: field_value
            })
        return json_value

    def migrate_information(self, related_model, related_model_class):
        # if impact_model.impact_model_information.technical_information:
        #     print("skipping migrationg technical information...")
        #     return
        value = self.generate_json_value(related_model, related_model_class._meta.get_fields())
        return value


    def handle(self, *args, **options):
        
        for impact_model in ImpactModel.objects.all():
            print("{} start migration ...".format(impact_model))
            technical_information = self.migrate_information(impact_model.technicalinformation, TechnicalInformation)
            input_data_information = self.migrate_information(impact_model.inputdatainformation, InputDataInformation)
            other_information = self.migrate_information(impact_model.otherinformation, OtherInformation)
            sector_class = apps.get_model('climatemodels', impact_model.base_model.sector.class_name)
            if hasattr(impact_model, impact_model.base_model.sector.class_name.lower()):
                # there are models without an related sector specific model created yet
                impact_model_sector = getattr(impact_model, impact_model.base_model.sector.class_name.lower())
                sector_specific_information = self.migrate_information(impact_model_sector, sector_class)
                if impact_model_sector.data:
                    sector_specific_information.update(
                        impact_model_sector.data
                    )
                impact_model.impact_model_information.sector_specific_information = sector_specific_information
            impact_model.impact_model_information.technical_information = technical_information
            impact_model.impact_model_information.input_data_information = input_data_information
            impact_model.impact_model_information.other_information = other_information
            impact_model.impact_model_information.save()