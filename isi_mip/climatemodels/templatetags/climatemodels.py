from django import template
from django.template.loader import render_to_string
from wagtail.models import Site

from isi_mip.climatemodels.models import (INFORMATION_TYPE_CHOICES,
                                          ImpactModelQuestion)
from isi_mip.core.models import HeaderLinks

register = template.Library()


@register.simple_tag(takes_context=True)
def progress_bar(context, **kwargs):
    impact_model = context['impact_model']
    count_questions = 0
    count_answers = 0
    for information_type, name in INFORMATION_TYPE_CHOICES:
        if information_type == 'sector_specific_information':
            information = ImpactModelQuestion.objects.filter(sector=impact_model.base_model.sector).first()
        else:
            information = ImpactModelQuestion.objects.filter(information_type=information_type).first()
        if information:
            for fieldset in information.question_group_list:
                values = []
                for field in fieldset[1]['fields']:
                    count_questions += 1
                    verbose_name = field['verbose_name']
                    value = getattr(impact_model.impact_model_information, information_type).get(field['name'], None)
                    if value or value == False:
                        count_answers += 1
    progress = count_questions and int(count_answers / count_questions * 100) or 0
    template = 'widgets/progress-bar.html'
    return render_to_string(template, context={'progress': progress, 'count_questions': count_questions, 'count_answers': count_answers})
