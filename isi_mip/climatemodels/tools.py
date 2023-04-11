from collections import OrderedDict

import xlsxwriter
from django.db.models import (ForeignKey, ManyToManyField, ManyToManyRel,
                              ManyToOneRel)

from isi_mip.climatemodels.models import (INFORMATION_TYPE_CHOICES,
                                          BaseImpactModel, ImpactModel,
                                          ImpactModelInformation,
                                          ImpactModelQuestion,
                                          InputDataInformation,
                                          OtherInformation, Sector,
                                          SectorInformationField,
                                          TechnicalInformation)

EMPTY_SECTORS = [
    'Agro-Economic Modelling',
    'Biodiversity',
    'Coastal Infrastructure',
    'Computable General Equilibrium Modelling',
    'Health',
    'Permafrost',
]

SKIP_FIELDS = [
    'id',
    'base_model',
    'public',
    'index_entries',
    'impact_model',
    'impact_model_responsible',
    'technicalinformation',
    'inputdatainformation',
    'otherinformation',
    'genericsector',
    'agriculture',
    'biomes',
    'forests',
    'fire',
    'energy',
    'marineecosystemsglobal',
    'marineecosystemsregional',
    'waterglobal',
    'waterregional',
    'biodiversity',
    'health',
    'coastalinfrastructure',
    'permafrost',
    'computablegeneralequilibriummodelling',
    'agroeconomicmodelling',
    'outputdata',
    'confirmation',
    'contactperson',
    'attachment',
    'impact_model_information',
]

SORT_ORDER = {
    "impact_model_responsible": 1,
    "main_reference_paper": 1,
    "other_references": 2,
}


class ImpactModelToXLSX:
    # https://xlsxwriter.readthedocs.org/en/latest/
    def __init__(self, res, qs):
        self.workbook = xlsxwriter.Workbook(res, {'in_memory': True})
        self.qs = qs
        self.xlsxdings()

    def get_field_data(self, model, field_name):
        field = model._meta.get_field(field_name)
        if isinstance(field, ManyToManyField):
            data = ", ".join(["%s" % i for i in getattr(model, field_name).all()])
        elif isinstance(field, ManyToOneRel) or isinstance(field, ManyToManyRel):
            try:
                data = ", ".join(["%s" % i for i in getattr(model, "%s_set" % field_name).all()])
            except AttributeError:
                data = ", ".join(["%s" % i for i in getattr(model, "%s" % field_name).all()])

        else:
            data = getattr(model, field_name) or ''
        return data

    def xlsxdings(self):
        general = self.workbook.add_worksheet('General Information')
        general.set_column('A:A', 20)
        bold = self.workbook.add_format({'bold': True})
        models = [BaseImpactModel, ImpactModel]
        model_fields = OrderedDict()
        all_field_titles = []
        for model in models:
            fields = model._meta.get_fields()
            filtered_fields = [field for field in fields if field.name not in (SKIP_FIELDS)]
            filtered_fields.sort(key=lambda val: SORT_ORDER[val.name] if val.name in SORT_ORDER else 0)
            model_fields[model.__name__] = {
                'class': model,
                'fields': [f.name for f in filtered_fields],
            }
            for field in filtered_fields:
                if hasattr(field, 'verbose_name'):
                    all_field_titles.append(field.verbose_name.capitalize())
                else:
                    if field.name == 'impact_model_responsible':
                        all_field_titles.append('Person responsible')
                    else:
                        name = field.name.replace("_", " ").capitalize()
                        all_field_titles.append(name)
        for information_type, name in INFORMATION_TYPE_CHOICES:
            if information_type == 'sector_specific_information':
                continue
            model = ImpactModelQuestion.objects.get(information_type=information_type, sector__isnull=True)
            fields = model.fields
            filtered_fields = [field for field in fields if field.get('name') not in (SKIP_FIELDS)]
            filtered_fields.sort(key=lambda val: SORT_ORDER[val.get('name')] if val.get('name') in SORT_ORDER else 0)
            all_field_titles = all_field_titles + [field.get('verbose_name') for field in filtered_fields]
            model_fields[information_type] = {
                'fields': filtered_fields,
            }
        general.write_row(0, 0, data=all_field_titles, cell_format=bold)

        for i, impact_model in enumerate(self.qs[:1]):
            for j, field in enumerate(model_fields['BaseImpactModel']['fields']):
                data = self.get_field_data(impact_model.base_model, field)
                general.write(i + 1, j, str(data))
            for j, field in enumerate(model_fields['ImpactModel']['fields'], start=j + 1):
                data = self.get_field_data(impact_model, field)
                general.write(i + 1, j, str(data))
            for information_type, name in INFORMATION_TYPE_CHOICES:
                if information_type == 'sector_specific_information':
                    continue
                information = getattr(impact_model.impact_model_information, information_type)
                for j, field in enumerate(model_fields[information_type]['fields'], start=j + 1):
                    value = model.get_field_value(field.get('field_type') , information.get(field.get('name'), None), make_pretty=False)
                    general.write(i + 1, j, str(value))

        for sector in Sector.objects.all():
            fields = []
            impact_model_questions = ImpactModelQuestion.objects.filter(sector=sector).first()
            if not impact_model_questions or not impact_model_questions.questions:
                continue
            # if not impact_model_questions.questions:
            #     continue
            # elif not sector.model.objects.filter(impact_model__in=self.qs).exists():
            #     continue
            # else:
            #     fields = [field.name for field in sector.model._meta.fields if field.name not in ('id', 'data')]
            fields = impact_model_questions.fields
            sector_name = 'M. E. and Fisheries (regional)' if sector.name == 'Marine Ecosystems and Fisheries (regional)' else sector.name
            sector_name = 'M. E. and Fisheries (global)' if sector.name == 'Marine Ecosystems and Fisheries (global)' else sector.name
            for ch in ['[', ']', ':', '*', '?', '/', '\\']:
                if ch in sector_name:
                    sector_name = sector_name.replace(ch, '-')
            sectorsheet = self.workbook.add_worksheet(sector_name[0:31])
            header_row = ['Impact Model'] + [x.get('verbose_name') for x in fields]
            sectorsheet.write_row(0, 0, data=header_row, cell_format=bold)
            for i, impact_model in enumerate(ImpactModel.objects.filter(base_model__sector=sector)):
                sectorsheet.write(i + 1, 0, str(impact_model))
                information = impact_model.impact_model_information.sector_specific_information

                for j, field in enumerate(fields):
                    value = impact_model_questions.get_field_value(field.get('field_type') , information.get(field.get('name'), None), make_pretty=False)
                    sectorsheet.write(i + 1, j + 1, str(value))

        self.workbook.close()


class ParticpantModelToXLSX:
    # https://xlsxwriter.readthedocs.org/en/latest/
    def __init__(self, res, qs):
        self.workbook = xlsxwriter.Workbook(res, {'in_memory': True})
        self.qs = qs
        self.process_xlsx()

    def process_xlsx(self):
        general = self.workbook.add_worksheet('Participants')
        general.set_column('A:A', 20)
        bold = self.workbook.add_format({'bold': True})
        header = ['Name', 'Email', 'Instiute', 'Country', 'Model', 'Sector', 'Comment']
        general.write_row(0, 0, data=header, cell_format=bold)
        for i, participant in enumerate(self.qs):
            general.write(i + 1, 0, participant.userprofile.name)
            general.write(i + 1, 1, participant.email)
            general.write(i + 1, 2, participant.userprofile.institute)
            general.write(i + 1, 3, participant.userprofile.country and participant.userprofile.country.name or '')
            models = [str(model) for model in participant.userprofile.responsible.all()]
            general.write(i + 1, 4, ", ".join(models))
            sectors = [sector.name for sector in participant.userprofile.sector.all()]
            general.write(i + 1, 5, ", ".join(sectors))
            general.write(i + 1, 6, participant.userprofile.comment)
        self.workbook.close()
