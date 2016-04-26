from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from wagtail.wagtailcore.models import Page

from isi_mip.climatemodels.forms import ImpactModelForm, ImpactModelStartForm, ContactPersonFormset, get_sector_form
from isi_mip.climatemodels.models import ImpactModel, InputData
from isi_mip.climatemodels.tools import ImpactModelToXLSX


class Assign(SuccessMessageMixin, UpdateView):
    template_name = 'climatemodels/assign.html'
    form_class = ImpactModelStartForm
    model = ImpactModel
    success_message = 'The model has been successfully created and assigned'

    def get_success_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']
        return reverse('admin:auth_user_list')

    def get_object(self, queryset=None):
        if 'username' in self.kwargs:
            user = User.objects.get(username=self.kwargs['username'])
            return ImpactModel(owner=user)
        return None


def impact_model_details(page, request, id):
    im = ImpactModel.objects.get(id=id)
    im_values = im.values_to_tuples() + im.fk_sector.values_to_tuples()
    model_details = []
    for k, v in im_values:
        if any((y for x, y in v)):
            res = {'term': k,
                   'definitions': ({'text': "<i>%s</i>: %s" % (x, y)} for x, y in v if y)
                   }
            model_details.append(res)
    model_details[0]['opened'] = True

    description = '<b>TODO</b> Intro Text unde omnis iste natus error sit voluptatem accusantium totam.'  # TODO: THIS IS STATIC
    context = {
        'page': page,
        'subpage': Page(title='Impact Model: %s' % im.name),
        'description': description,
        'headline': im.name,
        'list': model_details,
    }
    if request.user == im.owner:
        context['editlink'] = '<a href="{}">edit</a>'.format(
            page.url + page.reverse_subpage('edit', args=(im.id,)))
    if request.user.is_superuser:
        context['editlink'] += ' | <a href="{}">admin edit</a>'.format(
            urlresolvers.reverse('admin:climatemodels_impactmodel_change', args=(im.id,)))

    template = 'climatemodels/details.html'
    return render(request, template, context)

def impact_model_download(page, request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="ImpactModels {:%Y-%m-%d}.xlsx"'.format(datetime.now())
    ImpactModelToXLSX(response, qs=ImpactModel.objects.all())
    return response

def impact_model_edit(page, request, id):
    impactmodel = ImpactModel.objects.get(id=id)
    context = {'page': page, 'subpage': Page(title='Impact Model: %s' % impactmodel.name)}

    if request.method == 'POST':
        form = ImpactModelForm(request.POST, instance=impactmodel)
        contactform = ContactPersonFormset(request.POST, instance=impactmodel)
        form.do_the_thing()
        if form.is_valid():
            form.save()
            contactform.save()
            messages.success(request, "Changes to your model have been saved successfully.")
            target_url = page.url + page.reverse_subpage('edit_sector', args=(impactmodel.id,))
            return HttpResponseRedirect(target_url)
            #return impact_model_sector_edit(page, request, id)
        else:
            messages.warning(request, form.errors)
    else:
        form = ImpactModelForm(instance=impactmodel)
        contactform = ContactPersonFormset(instance=impactmodel)
    context['form'] = form
    context['cform'] = contactform
    template = 'climatemodels/edit.html'
    return render(request, template, context)

def impact_model_sector_edit(page, request, id):
    impactmodel = ImpactModel.objects.get(id=id)

    context = {'page': page, 'subpage': Page(title='Impact Model: %s' % impactmodel.name)}
    formular = get_sector_form(impactmodel.fk_sector_name)
    if request.method == 'POST':
        form = formular(request.POST, instance=impactmodel.fk_sector)
        form.do_the_thing()
        if form.is_valid():
            form.save()
            messages.success(request, "Changes to your model have been saved successfully.")
        else:
            messages.warning(request, form.errors)
    else:
        form = formular(instance=impactmodel.fk_sector)
    context['form'] = form
    template = 'climatemodels/edit_{}.html'.format(impactmodel.fk_sector_name)
    return render(request, template, context)


def input_data_details(page, request, id):
    data = InputData.objects.get(id=id)
    template = 'pages/input_data_details_page.html'

    description = '<b>TODO</b> Intro Text unde omnis iste natus error sit voluptatem accusantium totam.'  # TODO: THIS IS STATIC
    if request.user.is_superuser:
        description += ' | <a href="{}">admin edit</a>'.format(
            urlresolvers.reverse('admin:climatemodels_inputdata_change', args=(data.id,)))

    context = {'page': page,
               'subpage': Page(title='Input Data Set: %s' % data),
               'description': description,
               'list': [
                   {
                       'notoggle': True,
                       'opened': True,
                       # 'term': data.name, # TODO: Tom schau mal hier.
                       'definitions': [
                           {'text': 'Data Type: %s' % data.data_type},
                           {'text': 'Scenario: %s' % data.scenario},
                           {'text': 'Phase: %s' % data.phase},
                           {'text': 'Variables: %s' % ', '.join((x.as_span() for x in data.variables.all()))},
                       ]
                   },
                   {'notoggle': True, 'opened': True, 'term': 'Description',
                    'definitions': [{'text': data.description}]},
                   {'notoggle': True, 'opened': True, 'term': 'Caveats', 'definitions': [{'text': data.caveats}]},
                   {'notoggle': True, 'opened': True, 'term': 'Download Instructions', 'definitions': [{'text': data.download_instructions}]},
               ]
               }
    return render(request, template, context)