
import itertools
from typing import List, Optional

from django import forms
from django.db.models import F, Model, QuerySet
from django.forms.widgets import CheckboxSelectMultiple, Select
from django.utils.functional import cached_property
from wagtail.blocks import FieldBlock, StructBlock
from wagtail.blocks.field_block import BooleanBlock, CharBlock
from wagtail.blocks.field_block import \
    MultipleChoiceBlock as _MultipleChoiceBlock
from wagtail.blocks.field_block import RichTextBlock, TextBlock
from wagtail.blocks.list_block import ListBlock
from wagtail.coreutils import resolve_model_string


class BaseQuestionBlock(StructBlock):
    name = CharBlock(required=True, help_text='A unique name identifier for the question')
    question = TextBlock(required=True, help_text='The question you would like to ask')
    required = BooleanBlock(required=False, help_text='Is the question you are asking mandatory')
    help_text = TextBlock(required=False)


class TextareaQuestionBlock(BaseQuestionBlock):
    class Meta:
        template = 'impact_model_blocks/text_question_block.html'

        
class SingleLineQuestionBlock(BaseQuestionBlock):
    class Meta:
        template = 'impact_model_blocks/text_question_block.html'


class TrueFalseBlock(BaseQuestionBlock):
    nullable = BooleanBlock(required=False)


class ChoiceBlock(StructBlock):
    name = CharBlock(required=True)
    label = CharBlock(required=True)


class SingleChoiceBlock(BaseQuestionBlock):
    allow_custom = BooleanBlock(required=False)
    choices = ListBlock(ChoiceBlock)
    
    class Meta:
        template = 'impact_model_blocks/choice_block.html'
        label = 'Single-Choice'

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


class InputDataChoiceBlock(BaseQuestionBlock):
    # input_data = ModelMultipleChoiceBlock(
    #     target_model="climatemodels.InputData",
    #     queryset=get_input_data,
    # )
    choices = _MultipleChoiceBlock(
        required=True,
        choices=get_input_data,
        widget=CheckboxSelectMultiple
    )

    class Meta:
        template = 'impact_model_blocks/input_data_choice_block.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        # for input_data in value['input_data']:
        #     raise Exception(input_data)
        from isi_mip.climatemodels.models import InputData
        context['options'] = [{'label': input_data.name, 'id': input_data.pk} for input_data in InputData.objects.filter(pk__in=value['choices'])]
        return context




IMPACT_MODEL_QUESTION_BLOCKS = [
    ('single_line', SingleLineQuestionBlock()),
    ('textarea', TextareaQuestionBlock()),
    ('choice', SingleChoiceBlock()),
    ('multiple_choice', MultipleChoiceBlock()),
    ('input_data_choice', InputDataChoiceBlock()),
    ('true_false', TrueFalseBlock()),
]


# class FieldsetBlock(StructBlock):
#     heading = CharBlock(required=False)
#     text = RichTextBlock(required=False)
#     questions = ListBlock(IMPACT_MODEL_QUESTION_BLOCKS)
