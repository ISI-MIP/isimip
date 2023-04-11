import json
import logging
import re
import urllib.request
from datetime import date

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.db.models.fields import BooleanField, CharField, TextField
from django.db.models.fields.related import ManyToManyField
from wagtail.rich_text import RichText

from isi_mip.choiceorotherfield.models import ChoiceOrOtherField
from isi_mip.climatemodels.impact_model_blocks import (
    IMPACT_MODEL_QUESTION_BLOCKS, ModelSingleChoiceFieldBlock)
from isi_mip.climatemodels.models import (
    Agriculture, AgroEconomicModelling, Biodiversity, Biomes, BiomesForests, DataType,
    CoastalInfrastructure, ComputableGeneralEquilibriumModelling, Energy, Fire,
    Forests, Health, ImpactModelQuestion, InputDataInformation,
    MarineEcosystemsGlobal, MarineEcosystemsRegional, OtherInformation,
    Permafrost, Sector, SectorInformationGroup, TechnicalInformation,
    WaterGlobal, WaterRegional)
from isi_mip.pages.models import HomePage
from isi_mip.climatemodels.management.commands._model_field_definitions import MODEL_FIELD_DEFINITION, MODEL_FIELD_DATA_TYPE_MAPPING

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

FIELD_TO_STREAMFIELD_MAP = {
    'spatial_aggregation': ModelSingleChoiceFieldBlock
}

class Command(BaseCommand):
    help = 'Migrates the model documentation to the new dynamic and flexible format'

    def get_stream_field_type(self, stream_field):
        for k, v in IMPACT_MODEL_QUESTION_BLOCKS:
            if v.__class__ == stream_field.__class__:
                return k

    def get_stream_field(self, field):
        value = {
            'name': field.name,
            'question': field.verbose_name.capitalize(),
            'help_text': field.help_text,
            'required': not field.blank,

        }
        if field.name == 'spatial_aggregation':
            value.update({
                'model_choice': 'spatial_aggregation',
                'allow_custom': True
            })
            return {
                'type': 'model_single_choice',
                'value': value
            }
        elif field.name == 'climate_variables':
            return {
                'type': 'climate_variable_choice',
                'value': value
            }
        elif field.name == 'model_output':
            return {
                'type': 'biodiversity_model_output_choice',
                'value': value
            }
        elif field.__class__ == ManyToManyField:
            data_type_name = MODEL_FIELD_DATA_TYPE_MAPPING.get(field.name)
            print('data_type_name', data_type_name)
            # raise Exception(data_type_name)
            value.update({
                'data_type': DataType.objects.get(name=data_type_name).pk,
            })
            return {
                'type': 'input_data_choice',
                'value': value
            }
        elif field.__class__ == ChoiceOrOtherField:
            choices = [{'name': choice[0], 'label': choice[1]} for choice in field.choices]
            value.update({
                'allow_custom': True,
                'choices': choices
            })
            return {
                'type': 'choice',
                'value': value
            }
        elif field.__class__ == TextField:
            return {
                'type': 'textarea',
                'value': value
            }
        elif field.__class__ == BooleanField:
            return {
                'type': 'true_false',
                'value': value
            }
        elif field.__class__ == CharField and field.choices:
            choices = [{'name': choice[0], 'label': choice[1]} for choice in field.choices]
            value.update({
                'allow_custom': False,
                'choices': choices
            })
            return {
                'type': 'choice',
                'value': value
            }
        raise Exception(field)

        # "choices":[{"id":"489b21da-0673-422e-9d5b-c48e405c6417","type":"item","value":{"name":"asdf","label":"asdf"}},{"id":"2759513a-9f4e-40df-ad3e-ea326814d20d","type":"item","value":{"name":"asfd","label":"asdf"}}],"question":"asdf","required":false,"help_text":"","allow_custom":true}}]
        # raise Exception(field.__class__)


    def generate_stream_field(self, field):
        stream_field = self.get_stream_field(field)
        # stream_field.name = field.name
        # stream_field.question = field.verbose_name or field.name
        # stream_field.help_text = field.help_text
        # raise Exception(stream_field.value_from_datadict())
        # raise Exception((stream_field_type, stream_field))
        return stream_field

    def handle(self, *args, **options):
        ImpactModelQuestion.objects.all().delete()
        for model_type, model in MODEL_LIST:
            fieldsets = []
            impact_model_question = ImpactModelQuestion.objects.filter(Q(information_type=model_type) | Q(sector__slug=model_type))
            if impact_model_question.exists():
                print('skipping ImpactModelQuestion {}, already exists.'.format(impact_model_question.first()))
                continue
            else:
                print("Start migrating {} {} ...".format(model_type, model))
                information_type = model_type
                sector = Sector.objects.filter(slug=model_type).first()
                if sector:
                    information_type = None
                impact_model_question = ImpactModelQuestion.objects.create(
                    information_type=information_type,
                    sector=sector,
                )
            for model_fieldset in MODEL_FIELD_DEFINITION.get(model_type):
                questions = []
                fieldset = {
                    'type': 'fieldset',
                    'value': {
                        'heading': model_fieldset['heading'],
                        'description': model_fieldset['description'],
                        'questions': [],
                    }
                }
                for field in model_fieldset['fields']:
                    if field in IGNORE_FIELD_NAME_LIST:
                        print("skip field {}".format(field))
                        continue
                    block = self.generate_stream_field(model._meta.get_field(field))
                    if block:
                        questions.append(block)
                # raise Exception(questions)
                # impact_model_question.questions.append(('paragraph', RichText("<p>And they all lived happily ever after.</p>")))
                fieldset['value']['questions'] = questions
                fieldsets.append(fieldset)
            if sector:
                for group in SectorInformationGroup.objects.filter(sector=sector):
                    fieldset = {}
                    generic_fields = []
                    for field in group.fields.all():
                        form_field = TextField(name=field.unique_identifier, verbose_name=field.name, help_text=field.help_text, blank=True)
                        block = self.generate_stream_field(form_field)
                        generic_fields.append(block)
                    fieldset = {
                        'type': 'fieldset',
                        'value': {
                            'heading': group.name,
                            'description': group.description,
                            'questions': generic_fields,
                        }
                    }
                    fieldsets.append(fieldset)
            impact_model_question.questions = json.dumps(fieldsets, cls=DjangoJSONEncoder)
            impact_model_question.save()
            # raise Exception(questions)
            # raise Exception('here')
