
import itertools
from typing import List, Optional

from django import forms
from django.db.models import F, Model, QuerySet
from django.forms.widgets import CheckboxSelectMultiple, Select
from django.utils.functional import cached_property
from wagtail.blocks import FieldBlock, StructBlock
from wagtail.blocks.field_block import BooleanBlock, CharBlock
from wagtail.blocks.field_block import ChoiceBlock as _ChoiceBlock
from wagtail.blocks.field_block import \
    MultipleChoiceBlock as _MultipleChoiceBlock
from wagtail.blocks.field_block import RichTextBlock, TextBlock
from wagtail.blocks.list_block import ListBlock
from wagtail.core.blocks.stream_block import StreamBlock
from wagtail.coreutils import resolve_model_string


class BaseQuestionBlock(StructBlock):
    name = CharBlock(required=True, help_text='A unique name identifier for the question')
    question = TextBlock(required=True, help_text='The question you would like to ask')
    required = BooleanBlock(required=False, help_text='Is the question you are asking mandatory')
    help_text = TextBlock(required=False)


class TextareaQuestionBlock(BaseQuestionBlock):
    class Meta:
        template = 'impact_model_blocks/text_question_block.html'
        label_format = '{name} (Text)'

        
class SingleLineQuestionBlock(BaseQuestionBlock):
    class Meta:
        template = 'impact_model_blocks/text_question_block.html'
        label_format = '{name} (Single-Line-Text)'


class TrueFalseBlock(BaseQuestionBlock):
    nullable = BooleanBlock(required=False)

    class Meta:
        label = 'True/False'
        label_format = '{name} (True/False)'


class ChoiceBlock(StructBlock):
    name = CharBlock(required=True)
    label = CharBlock(required=True)


class SingleChoiceBlock(BaseQuestionBlock):
    allow_custom = BooleanBlock(required=False)
    choices = ListBlock(ChoiceBlock)
    
    class Meta:
        template = 'impact_model_blocks/choice_block.html'
        label = 'Single-Choice'
        label_format = '{name} (Single-Choice)'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['options'] = value['choices']
        context['singleselect'] = False
        context['allowcustom'] = value['allow_custom']
        return context

    
class MultipleChoiceBlock(BaseQuestionBlock):
    # allow_custom = BooleanBlock(required=False)
    choices = ListBlock(ChoiceBlock)
    
    class Meta:
        template = 'impact_model_blocks/choice_block.html'
        label = 'Multiple-Choice'
        label_format = '{name} (Multiple-Choice)'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['options'] = value['choices']
        context['singleselect'] = False
        # context['allowcustom'] = value['allow_custom']
        return context
    



def get_input_data():
    from isi_mip.climatemodels.models import InputData
    # return InputData.objects.all()
    return [(input_data.pk, input_data.name) for input_data in InputData.objects.all()]


def get_data_type_choices():
    from isi_mip.climatemodels.models import DataType
    return [(data_type.pk, data_type.name) for data_type in DataType.objects.all()]


class InputDataChoiceBlock(BaseQuestionBlock):
    data_type = _ChoiceBlock(choices=get_data_type_choices)

    class Meta:
        template = 'impact_model_blocks/input_data_choice_block.html'
        label = 'Input-Data-Choice'
        label_format = '{name} ({data_type})'


class ClimateVariableChoiceBlock(BaseQuestionBlock):

    class Meta:
        template = 'impact_model_blocks/input_data_choice_block.html'
        label = 'Climate-Variable-Choice'
        label_format = '{name}'


class BiodiversityModelOutputChoiceBlock(BaseQuestionBlock):

    class Meta:
        template = 'impact_model_blocks/input_data_choice_block.html'
        label = 'Biodiversity-Model-Output-Choice'
        label_format = '{name}'

MODEL_CHOICES = [
    ('spatial_aggregation', 'Spatial Aggregation')
]


class ModelSingleChoiceFieldBlock(BaseQuestionBlock):
    allow_custom = BooleanBlock(required=False)
    model_choice = _ChoiceBlock(choices=MODEL_CHOICES)

    class Meta:
        label = 'Model-Single-Choice'
        label_format = '{name} ({model_choice})'


IMPACT_MODEL_QUESTION_BLOCKS = [
    ('single_line', SingleLineQuestionBlock()),
    ('textarea', TextareaQuestionBlock()),
    ('choice', SingleChoiceBlock()),
    ('multiple_choice', MultipleChoiceBlock()),
    ('input_data_choice', InputDataChoiceBlock()),
    ('climate_variable_choice', ClimateVariableChoiceBlock()),
    ('biodiversity_model_output_choice', BiodiversityModelOutputChoiceBlock()),
    ('model_single_choice', ModelSingleChoiceFieldBlock()),
    ('true_false', TrueFalseBlock()),
]


class FieldsetBlock(StructBlock):
    heading = CharBlock(required=False)
    description = RichTextBlock(required=False)
    questions = StreamBlock(IMPACT_MODEL_QUESTION_BLOCKS)
