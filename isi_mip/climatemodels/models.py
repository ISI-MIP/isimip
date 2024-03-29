import os
from collections import OrderedDict

import django
from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import JSONField
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_filters.fields import ChoiceField, MultipleChoiceField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from isi_mip.choiceorotherfield.fields import MyTypedChoiceField
from isi_mip.choiceorotherfield.models import ChoiceOrOtherField
from isi_mip.climatemodels.fields import MyModelSingleChoiceField
from isi_mip.climatemodels.impact_model_blocks import (
    IMPACT_MODEL_QUESTION_BLOCKS, BiodiversityModelOutputChoiceBlock,
    FieldsetBlock)
from isi_mip.climatemodels.widgets import MyBooleanSelect, MyMultiSelect
from isi_mip.sciencepaper.models import Paper


def generate_helptext(help_text, value):
    return "<abbr title='{}'>{}</abbr>".format(help_text, value)


class Region(models.Model):
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class SimulationRound(models.Model):
    name = models.CharField(max_length=500, unique=True)
    slug = models.SlugField()
    order = models.SmallIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-order',)


class ReferencePaper(Paper):
    def __str__(self):
        # if self.doi:
        #     return "%s (<a target='_blank' href='http://dx.doi.org/%s'>%s</a>)" % (self.title, self.doi, self.doi)
        return self.title

    def title_with_link(self):
        if self.doi:
            return "<a target='_blank' href='http://dx.doi.org/{0.doi}'>{0.title}</a>".format(self)
        return self.title

    def entry_with_link(self):
        author = "{} et al. ".format(self.lead_author) if self.lead_author else ''
        title = "<a target='_blank' href='http://dx.doi.org/{0.doi}'>{0.title}</a>. ".format(self) if self.doi else self.title
        journal = "{0.journal_name},{0.journal_volume},{0.journal_pages},".format(self) if self.journal_name else ''
        year = self.first_published.year if self.first_published else ''
        return "{}{}{}{}".format(author, title, journal, year)

    def entry(self):
        author = "{} et al. ".format(self.lead_author) if self.lead_author else ''
        title = "{0.title}. ".format(self) if self.doi else self.title
        journal = "{0.journal_name},{0.journal_volume},{0.journal_pages},".format(self) if self.journal_name else ''
        year = self.first_published.year if self.first_published else ''
        return "{}{}{}{}".format(author, title, journal, year)


class DataType(models.Model):
    name = models.CharField(max_length=500, unique=True)
    is_climate_data_type = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class ClimateVariable(models.Model):
    name = models.CharField(max_length=500, unique=True)
    abbreviation = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        if self.abbreviation:
            return '{0.name} ({0.abbreviation})'.format(self)
        return self.name

    def as_span(self):
        if self.abbreviation:
            return '<abbr title="{0.name}">{0.abbreviation}</abbr>'.format(self)
        return self.name

    def pretty(self):
        return self.as_span()

    class Meta:
        ordering = ('name',)


class SocioEconomicInputVariables(models.Model):
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Socio-economic input variable'
        ordering = ('name', )


class Scenario(models.Model):
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class SpatialAggregation(models.Model):
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class ContactPerson(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    institute = models.CharField(max_length=500, null=True, blank=True)
    base_impact_model = models.ForeignKey('BaseImpactModel', on_delete=models.CASCADE,  null=True, blank=True)

    def __str__(self):
        return "%s%s %s" % (self.name, self.institute and " (%s)" % self.institute or "", self.email)

    def pretty(self):
        return "<a href='mailto:{0.email}'>{0.email}</a>, {0.institute}".format(self)

    class Meta:
        ordering = ('name',)


class InputData(models.Model):
    PROTOCOL_DATA = 'P'
    SECONDARY_DATA = 'S'
    PROTOCOL_RELATION_CHOICES = (
        (PROTOCOL_DATA, 'Protocol'),
        (SECONDARY_DATA, 'Secondary'),
    )
    name = models.CharField(max_length=500, unique=True)
    data_type = models.ForeignKey(DataType, null=True, blank=True, on_delete=models.SET_NULL)
    protocol_relation = models.CharField(max_length=1, choices=PROTOCOL_RELATION_CHOICES, default=PROTOCOL_DATA)
    scenario = models.ManyToManyField(Scenario, blank=True, related_name='scenarios')
    variables = models.ManyToManyField(ClimateVariable, blank=True, help_text="The variables are filtered based on the data type. To see variables of a different data type, please change and save data type first.")
    simulation_round = models.ManyToManyField(SimulationRound, blank=True, related_name='simulationrounds')
    description = models.TextField(null=True, blank=True, default='')
    specification = models.TextField(null=True, blank=True, default='')
    data_source = models.TextField(null=True, blank=True, default='')
    caveats = models.TextField(null=True, blank=True)
    download_instructions = models.TextField(null=True, blank=True, default='')
    data_link = models.URLField(null=True, blank=True, help_text="Link to the https://data.isimip.org/ repository.")
    doi_link = models.URLField(null=True, blank=True, help_text="Link to the https://doi.org system.")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s (%s)' % (self.name, ", ".join(self.simulation_round.values_list('name', flat=True)))

    class Meta:
        verbose_name_plural = 'Input data'
        ordering = ('-created', 'name',)

    def pretty(self):
        from isi_mip.pages.models import GettingStartedPage
        page = GettingStartedPage.objects.get(is_input_data_parent_page=True)
        url = page.url + page.reverse_subpage('details', kwargs={'id': self.pk})
        pretty = "<a href='{url}'>{name}</a>".format(name=self.name, url=url)
        return pretty


class Sector(models.Model):
    name = models.CharField(max_length=500, unique=True)
    slug = models.SlugField()
    drkz_folder_name = models.CharField(max_length=500, verbose_name="DKRZ folder name")
    SECTOR_MAPPING = (
        ('GenericSector', 'Generic Sector'),
        ('Agriculture', 'Agriculture'),
        ('Energy', 'Energy'),
        ('WaterGlobal', 'Water (global)'),
        ('WaterRegional', 'Water (regional)'),
        ('Biomes', 'Biomes'),
        ('Fire', 'Fire'),
        ('Forests', 'Forests'),
        ('MarineEcosystemsGlobal', 'Marine Ecosystems and Fisheries (global)'),
        ('MarineEcosystemsRegional', 'Marine Ecosystems and Fisheries (regional)'),
        ('Biodiversity', 'Biodiversity'),
        ('Health', 'Health'),
        ('CoastalInfrastructure', 'Coastal Infrastructure',),
        ('Permafrost', 'Permafrost'),
        ('ComputableGeneralEquilibriumModelling', 'Computable General Equilibrium Modelling'),
        ('AgroEconomicModelling', 'Agro-Economic Modelling'),
    )
    class_name = models.CharField(max_length=500, choices=SECTOR_MAPPING, default='GenericSector')
    has_sector_specific_values = models.BooleanField(default=True)

    @property
    def model(self):
        return apps.get_model(app_label='climatemodels', model_name=self.class_name)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Sectors'
        ordering = ('name',)


class SectorInformationGroup(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    identifier = models.SlugField()
    description = models.TextField(blank=True)
    order = models.SmallIntegerField(default=0)

    def __str__(self):
        return '%s (%s)' % (self.name, self.sector.name)

    class Meta:
        verbose_name_plural = 'Sector information groups'
        ordering = ('order', 'name')
        unique_together = ('sector', 'name')


class SectorInformationField(models.Model):
    information_group = models.ForeignKey(SectorInformationGroup, on_delete=models.CASCADE,  related_name='fields')
    name = models.CharField(max_length=500)
    identifier = models.SlugField()
    help_text = models.CharField(max_length=500, blank=True)
    order = models.SmallIntegerField(default=0)

    def __str__(self):
        return '%s' % (self.name, )

    class Meta:
        verbose_name_plural = 'Sector information fields'
        ordering = ('order', 'name')
        unique_together = ('name', 'information_group')

    @property
    def unique_identifier(self):
        return '%s-%s' % (self.information_group.identifier, self.identifier)


class BaseImpactModel(index.Indexed, models.Model):
    name = models.CharField(max_length=500)
    drkz_folder_name = models.CharField(max_length=500, verbose_name="DKRZ folder name")
    SECTOR_CHOICES = (
        ('Agriculture', 'Agriculture'),
        ('Agro-Economic Modelling', 'Agro-Economic Modelling'),
        ('Biodiversity', 'Biodiversity'),
        ('Biomes', 'Biomes'),
        ('Coastal Infrastructure', 'Coastal Infrastructure'),
        ('Computable General Equilibrium Modelling', 'Computable General Equilibrium Modelling'),
        ('Energy', 'Energy'),
        ('Forests', 'Forests'),
        ('Health', 'Health'),
        ('Marine Ecosystems and Fisheries (global)', 'Marine Ecosystems and Fisheries (global)'),
        ('Marine Ecosystems and Fisheries (regional)', 'Marine Ecosystems and Fisheries (regional)'),
        ('Permafrost', 'Permafrost'),
        ('Water (global)', 'Water (global)'),
        ('Water (regional)', 'Water (regional)'),
    )
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE,  help_text='The sector to which this information pertains. Some models may have further entries for other sectors.')
    region = models.ManyToManyField(Region, help_text="Region for which model produces results")
    short_description = models.TextField(
        null=True, blank=True, default='', verbose_name="Short model description (all rounds)",
        help_text="This short description should assist other researchers in getting an understanding of your model, including the main differences between model versions used for different ISIMIP simulation rounds.")

    search_fields = [
        index.SearchField('name', partial_match=True, boost=10),
        index.RelatedFields('sector', [
            index.SearchField('name'),
        ]),
        index.FilterField('public'),
        index.SearchField('short_description'),
        index.SearchField('get_related_contact_persons'),
    ]

    class Meta:
        ordering = ('name', 'sector')

    def __str__(self):
        return "%s (%s)" % (self.name, self.sector)

    def get_related_contact_persons(self):
        contact_persons = []
        for impact_model in self.impact_model.all():
            for owner in impact_model.impact_model_responsible.all():
                contact_persons.append('%s %s %s' % (owner.name, owner.email, owner.institute))
        return '\n'.join(contact_persons)

    def relative_url(self, site, request):
        # hard coded url, since no better solution at the moment
        # https://groups.google.com/forum/#!topic/wagtail/51FD2E4Odmc
        return "/impactmodels/details/%s/" % self.pk

    def get_missing_simulation_rounds(self):
        return SimulationRound.objects.exclude(id__in=self.impact_model.all().values_list('simulation_round', flat=True))

    def public(self):
        return self.impact_model.filter(public=True).exists()

    def can_duplicate_from(self):
        return self.impact_model.order_by('simulation_round').first()

    def _get_verbose_field_name(self, field):
        fieldmeta = self._meta.get_field(field)
        ret = fieldmeta.verbose_name.title()
        if fieldmeta.help_text:
            ret = generate_helptext(fieldmeta.help_text, ret)
        return ret

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        return [
            ('Common information', [
                (vname('sector'), self.sector),
                (vname('region'), ', '.join([x.name for x in self.region.all()])),
            ])]

    def save(self, *args, **kwargs):
        is_creation = self.pk is None
        super().save(*args, **kwargs)
        if not is_creation:
            # make sure if sector changes that sector specific objects exists for every impact model
            for impact_model in ImpactModel.objects.filter(base_model=self):
                if not hasattr(impact_model, impact_model.fk_sector_name):
                    self.sector.model.objects.get_or_create(impact_model=impact_model)


class ImpactModel(models.Model):
    base_model = models.ForeignKey(BaseImpactModel, null=True, blank=True, related_name='impact_model', on_delete=models.CASCADE)
    simulation_round = models.ForeignKey(
        SimulationRound, blank=True, null=True, on_delete=models.SET_NULL,
        help_text="The ISIMIP simulation round for which these model details are relevant"
    )
    version = models.CharField(max_length=500, null=True, blank=True, verbose_name='Model version',
                               help_text=mark_safe('Indicate this by a version number or year of application. If the model code would change or a new model application is performed, the new model version should be documented, and this change should be reflected in the simulation files. More information on model versioning you can find <a href="/protocol/preparing-simulation-files/" target="_blank">here</a>.'))
    model_license = models.CharField(max_length=200, null=True, blank=True, verbose_name='Model license')
    model_url = models.URLField(null=True, blank=True, verbose_name='Model Homepage',
                               help_text='The homepage of the model or a link to a git tree or hash of the model version used.')
    data_download = models.URLField(null=True, blank=True, verbose_name='Data download', help_text="Follow this link to access the datasets in the ISIMIP Repository.")
    doi = models.URLField(null=True, blank=True, verbose_name='DOI', help_text="For more information and how to cite this dataset, please follow the DOI.")
    main_reference_paper = models.ForeignKey(
        ReferencePaper, null=True, blank=True, related_name='main_ref', verbose_name='Reference paper: main reference',
        help_text="The single paper that should be cited when referring to simulation output from this model",
        on_delete=models.SET_NULL)
    other_references = models.ManyToManyField(ReferencePaper, blank=True, verbose_name='Reference paper: other references',
                                              help_text='Other papers describing aspects of this model')
    additional_persons_involved = models.CharField(max_length=500, null=True, blank=True, verbose_name='Additional persons involved',
                               help_text='List of all additional persons involved in this model.')
    simulation_round_specific_description = models.TextField(
        null=True, blank=True, default='', verbose_name="Simulation round specific description",
        help_text="")

    public = models.BooleanField(default=False)



    class Meta:
        unique_together = ('base_model', 'simulation_round')
        ordering = ('base_model', 'simulation_round')

    def __str__(self):
        return "%s (%s, %s)" % (self.base_model and self.base_model.name or self.id, self.base_model and self.base_model.sector or '', self.simulation_round)

    @property
    def model_output_license(self):
        if hasattr(self, 'confirmation'):
            return self.confirmation.confirmed_license
        return None


    @property
    def fk_sector_name(self):
        return self.base_model.sector.class_name.lower()

    @property
    def fk_sector(self):
        return getattr(self, self.fk_sector_name)

    def save(self, *args, **kwargs):
        is_duplication = kwargs.pop('is_duplication', False)
        is_creation = self.pk is None
        super().save(*args, **kwargs)
        if not is_duplication and is_creation:
            # if model gets duplicated we handle related instances in the duplicate method
            ImpactModelInformation.objects.get_or_create(impact_model=self)

        # make all owners involved in the duplicated model
        if is_creation and self.base_model:
            for owner in self.impact_model_responsible.all():
                owner.responsible.add(self)
        # make sure if sector changes that sector specific objects exists for the impact model

    def duplicate(self, simulation_round):
        # save old references
        old_impact_model_information = self.impact_model_information
        # Impact model
        duplicate = ImpactModel(
            base_model=self.base_model,
            simulation_round=simulation_round,
            version=self.version,
            main_reference_paper=self.main_reference_paper,
            additional_persons_involved=self.additional_persons_involved,
            simulation_round_specific_description=self.simulation_round_specific_description,
            public=True,
            data_download=self.data_download,
            doi=self.doi,

        )
        duplicate.save(is_duplication=True)
        duplicate.other_references.set(self.other_references.all())
        # Technical information
        old_impact_model_information.pk = None
        old_impact_model_information.impact_model = duplicate
        old_impact_model_information.save()
        return duplicate

    def _get_verbose_field_name(self, field):
        fieldmeta = self._meta.get_field(field)
        ret = fieldmeta.verbose_name
        if not ret.isupper():
            ret = ret.title()
        if fieldmeta.help_text:
            ret = generate_helptext(fieldmeta.help_text, ret)
        return ret

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        bvname = self.base_model._get_verbose_field_name
        cpers = [(x.name, x.pretty()) for x in self.impact_model_responsible.all()]
        if self.additional_persons_involved:
            cpers.append(['Additional persons involved', self.additional_persons_involved])
        if self.other_references.exists():
            other_references = "<ul>%s</ul>" % "".join(["<li>%s</li>" % x.entry_with_link() for x in self.other_references.all()])
        else:
            other_references = None
        return [
            ('Person responsible for model simulations in this simulation round', cpers),
            ('Basic information', [
                (vname('version'), self.version),
                (generate_helptext(mark_safe('Please note, if you want to update the model output license please <a href="mailto:info@isimip.org">write to us</a>.'), 'Model Output License'), self.model_output_license),
                (vname('model_url'), self.model_url),
                (vname('data_download'), self.data_download and "<a href='{0}' target='_blank'>{0}</a>".format(self.data_download)),
                (vname('doi'), self.doi and "<a href='{0}' target='_blank'>{0}</a>".format(self.doi)),
                (vname('model_license'), self.model_license),
                (vname('simulation_round_specific_description'), self.simulation_round_specific_description),
                (vname('main_reference_paper'),
                 self.main_reference_paper.entry_with_link() if self.main_reference_paper else None),
                (vname('other_references'), other_references),
            ]),
        ]

    def can_confirm_data(self):
        return hasattr(self, 'confirmation') and not self.confirmation.is_confirmed


class ImpactModelInformation(models.Model):
    impact_model = models.OneToOneField(
        ImpactModel,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='impact_model_information'
    )
    technical_information = JSONField(default=dict)
    input_data_information = JSONField(default=dict)
    other_information = JSONField(default=dict)
    sector_specific_information = JSONField(default=dict)

    def __str__(self):
        return "{}".format(self.impact_model)


    def values_to_tuples(self):
        tuples = []
        for information_type, name in INFORMATION_TYPE_CHOICES:
            if information_type == 'sector_specific_information':
                information = ImpactModelQuestion.objects.filter(sector=self.impact_model.base_model.sector).first()
            else:
                information = ImpactModelQuestion.objects.filter(information_type=information_type).first()
            if information:
                for fieldset in information.question_group_list:
                    values = []
                    for field in fieldset[1]['fields']:
                        verbose_name = field['verbose_name']
                        value = getattr(self, information_type).get(field['name'], None)
                        value = information.get_field_value(field['field_type'], value)
                        if value:
                            if field['help_text']:
                                verbose_name = generate_helptext(field['help_text'], verbose_name)
                            values.append((verbose_name, value))
                    tuples.append((fieldset[0], values))
        # raise Exception(tuples)
        return tuples




INFORMATION_TYPE_CHOICES = [
    ('technical_information', 'Resolution information'),
    ('input_data_information', 'Input data information'),
    ('other_information', 'Model setup Information'),
    ('sector_specific_information', 'Sector-specific information'),
]

@register_snippet
class ImpactModelQuestion(models.Model):
    information_type = models.CharField(choices=INFORMATION_TYPE_CHOICES, max_length=255, blank=True, null=True)
    sector = models.OneToOneField('Sector', blank=True, null=True, on_delete=models.PROTECT)
    step = models.PositiveSmallIntegerField(default=0)
    heading = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)
    questions = StreamField([('fieldset', FieldsetBlock())], blank=True, null=True, use_json_field=True)

    panels = [
        FieldPanel('information_type'),
        FieldPanel('sector'),
        FieldPanel('step'),
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('questions'),
    ]

    class Meta:
        ordering = ['information_type', 'sector', 'step']
        verbose_name = 'Model Documentation'
        constraints = [
            models.UniqueConstraint(fields=['information_type', 'sector'], name='unique_information_type_sector')
        ]

    def __str__(self):
        if self.sector:
            return self.sector.name
        if self.information_type:
            return self.information_type

    def get_form(self, *args, **kwargs):
        from isi_mip.climatemodels.forms import ImpactModelQuestionForm
        kwargs['impact_model_question'] = self
        return ImpactModelQuestionForm(*args, **kwargs)

    def get_field_options(self, question):
        field = question.value
        options = {"label": field['question']}
        options["help_text"] = field['help_text']
        options["required"] = field['required']
        # options["initial"] = field.default_value
        return options


    def create_field(self, question, simulation_round, fieldset):
        options = self.get_field_options(question)
        # options['fieldset'] = fieldset
        if question.block_type == 'textarea':
            return django.forms.CharField(widget=django.forms.Textarea, **options)
        elif question.block_type == 'single_line':
            return django.forms.CharField(**options)
        elif question.block_type == 'choice':
            choices = question.value['choices']
            options["choices"] = [(choice['label'], choice['name']) for choice in choices]
            return MyTypedChoiceField(widget=MyMultiSelect(allowcustom=question.value['allow_custom'], multiselect=False), **options)
        elif question.block_type == 'multiple_choice':
            choices = question.value['choices']
            options["choices"] = [(choice['label'], choice['name']) for choice in choices]
            return django.forms.MultipleChoiceField(widget=MyMultiSelect(multiselect=True), **options)
        elif question.block_type == 'model_single_choice':
            return MyModelSingleChoiceField(allowcustom=True, queryset=SpatialAggregation.objects.all())
        elif question.block_type == 'biodiversity_model_output_choice':
            choices = [(biodiversity.pk, biodiversity.name) for biodiversity in BiodiversityModelOutput.objects.all().distinct()]
            return django.forms.MultipleChoiceField(
                widget=MyMultiSelect(allowcustom=True, multiselect=True),
                choices=choices,
                **options)
        elif question.block_type == 'climate_variable_choice':
            choices = [(climate_variable.pk, climate_variable.name) for climate_variable in ClimateVariable.objects.filter(inputdata__data_type__is_climate_data_type=True, inputdata__simulation_round=simulation_round).distinct()]
            return django.forms.MultipleChoiceField(
                widget=MyMultiSelect(allowcustom=False, multiselect=True),
                choices=choices,
                **options)
        elif question.block_type == 'input_data_choice':
            data_type = question.value['data_type']
            choices = [(input_data.pk, input_data.name) for input_data in InputData.objects.filter(data_type__pk=data_type, simulation_round=simulation_round, protocol_relation=InputData.PROTOCOL_DATA)]
            return django.forms.MultipleChoiceField(
                widget=MyMultiSelect(allowcustom=False, multiselect=True),
                choices=choices,
                **options)
        elif question.block_type == 'true_false':
            return django.forms.BooleanField(widget=MyBooleanSelect(nullable=question.value['nullable']), **options)
        raise Exception(question.block_type)

    def get_field_value(self, field_type, values, make_pretty=True):
        if values is None:
            return ''
        if field_type == 'input_data_choice':
            return ", ".join([make_pretty and input_data.pretty() or str(input_data) for input_data in InputData.objects.filter(pk__in=values)])
        elif field_type == 'model_single_choice':
            return SpatialAggregation.objects.get(pk=values).name
        elif field_type == 'climate_variable_choice':
            return ", ".join([make_pretty and climate_variable.pretty() or str(climate_variable) for climate_variable in ClimateVariable.objects.filter(pk__in=values)])
        elif field_type == 'biodiversity_model_output_choice':
            return ", ".join([biodiversity.name for biodiversity in BiodiversityModelOutput.objects.filter(pk__in=values)])
        if type(values) is bool:
            return 'Yes' if values is True else 'No' if values is False else ''
        return values


    def formfields(self, simulation_round):
        formfields = OrderedDict()

        for fieldset in self.questions:
            for question in fieldset.value['questions']:
                fieldset_name = fieldset.value['heading']
                fieldset_description = fieldset.value['description']
                clean_name = question.value['name']
                formfields[clean_name] =  self.create_field(question, simulation_round, fieldset_name)
        return formfields

    @property
    def fields(self):
        fields = []
        for fieldset in self.questions:
            for question in fieldset.value['questions']:
                fields.append({
                    'name': question.value['name'],
                    'verbose_name': question.value['question'],
                    'help_text': question.value['help_text'],
                    'field_type': question.block_type,
                })
        return fields

    @property
    def fieldset(self):
        fieldset_list = []
        for fieldset in self.questions:
            fields = []
            for question in fieldset.value['questions']:
                fields.append(question.value['name'])
            # raise Exception(formfields)
            fieldset_list.append((fieldset.value['heading'], {
                'fields': fields,
                'description': fieldset.value['description'],
            }))
        return fieldset_list

    @property
    def question_group_list(self):
        fieldset_list = []
        for fieldset in self.questions:
            fields = []
            for question in fieldset.value['questions']:
                fields.append({
                    'name': question.value['name'],
                    'verbose_name': question.value['question'],
                    'help_text': question.value['help_text'],
                    'field_type': question.block_type,
                })
            # raise Exception(formfields)
            fieldset_list.append((fieldset.value['heading'], {
                'fields': fields,
                'description': fieldset.value['description'],
            }))
        return fieldset_list



class TechnicalInformation(models.Model):
    impact_model = models.OneToOneField(
        ImpactModel,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    spatial_aggregation = models.ForeignKey(SpatialAggregation, null=True, blank=True, on_delete=models.SET_NULL)
    spatial_resolution = ChoiceOrOtherField(
        max_length=500, choices=(('0.5’ x 0.5’', '0.5’ x 0.5’'), ('1.5’ x 1.5’', '1.5’ x 1.5’'), ('6.0’ x 6.0’', '5.0’ x 5.0’'),('0.5°x0.5°', '0.5°x0.5°'),), blank=True, null=True, verbose_name='Spatial Resolution',
        help_text="The spatial resolution at which the ISIMIP simulations were run, if on a regular grid. Data was provided on a 0.5°x0.5° grid")
    spatial_resolution_info = models.TextField(blank=True, verbose_name='Additional spatial aggregation & resolution information',
                                               help_text='Anything else necessary to understand the spatial aggregation and resolution at which the model operates')
    TEMPORAL_RESOLUTION_CLIMATE_CHOICES = (('annual', 'annual'), ('monthly', 'monthly'), ('daily', 'daily'), ('constant', 'constant'))
    temporal_resolution_climate = ChoiceOrOtherField(
        max_length=500, choices=TEMPORAL_RESOLUTION_CLIMATE_CHOICES, blank=True, null=True, verbose_name='Temporal resolution of input data: climate variables',
        help_text="ISIMIP data was provided in daily time steps. If more than one resolution is used, please include them in the custom field")
    temporal_resolution_co2 = ChoiceOrOtherField(
        max_length=500, choices=(('annual', 'annual'),), blank=True, null=True, verbose_name='Temporal resolution of input data: CO2',
        help_text="ISIMIP data was provided in annual time steps")
    temporal_resolution_land = ChoiceOrOtherField(
        max_length=500, choices=(('annual', 'annual'),), blank=True, null=True, verbose_name='Temporal resolution of input data: land use/land cover',
        help_text="ISIMIP data was provided in annual time steps")
    temporal_resolution_soil = ChoiceOrOtherField(
        max_length=500, choices=(('constant', 'constant'),), blank=True, null=True, verbose_name='Temporal resolution of input data: soil', help_text="ISIMIP data was fixed over time")
    temporal_resolution_info = models.TextField(
        verbose_name='Additional temporal resolution information', blank=True,
        help_text='Anything else necessary to understand the temporal resolution at which the model operates')

    def _get_verbose_field_name(self, field):
        fieldmeta = self._meta.get_field(field)
        ret = fieldmeta.verbose_name.title()
        if fieldmeta.help_text:
            ret = generate_helptext(fieldmeta.help_text, ret)
        return ret

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        return ('Resolution', [
                (vname('spatial_aggregation'), self.spatial_aggregation),
                (vname('spatial_resolution'), self.spatial_resolution),
                (vname('spatial_resolution_info'), self.spatial_resolution_info),
                (vname('temporal_resolution_climate'), self.temporal_resolution_climate),
                (vname('temporal_resolution_co2'), self.temporal_resolution_co2),
                (vname('temporal_resolution_land'), self.temporal_resolution_land),
                (vname('temporal_resolution_soil'), self.temporal_resolution_soil),
                (vname('temporal_resolution_info'), self.temporal_resolution_info),
                ])


class InputDataInformation(models.Model):
    impact_model = models.OneToOneField(
        ImpactModel,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    simulated_atmospheric_climate_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Simulated atmospheric climate data sets used",
                                                                     help_text="The simulated atmospheric climate data sets used in this simulation round", related_name="simulated_atmospheric_climate_data_sets")
    observed_atmospheric_climate_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Observed atmospheric climate data sets used",
                                                                    help_text="The observed atmospheric climate data sets used in this simulation round", related_name="observed_atmospheric_climate_data_sets")
    emissions_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Emissions data sets used",
                                                 help_text="The emissions data sets used in this simulation round", related_name="emissions_data_sets")
    socio_economic_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Socio-economic data sets used",
                                                      help_text="The socio-economic data sets used in this simulation round", related_name="socio_economic_data_sets")
    land_use_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Land use data sets used",
                                                help_text="The Land use data sets used in this simulation round", related_name="land_use_data_sets")
    other_human_influences_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Other human influences data sets used",
                                                              help_text="The other human influences data sets used in this simulation round", related_name="other_human_influences_data_sets")
    other_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Other data sets used",
                                             help_text="Other data sets used in this simulation round", related_name="other_data_sets")
    additional_input_data_sets = models.TextField(
        null=True, blank=True, verbose_name='Additional input data sets',
        help_text='Data sets used to drive the model that were not provided by ISIMIP'
    )
    climate_variables = models.ManyToManyField(
        ClimateVariable, blank=True, verbose_name='Climate variables',
        help_text="Which of the climate input variables provided was used by your model?")
    climate_variables_info = models.TextField(blank=True, verbose_name='Additional information about input variables',
                                              help_text='Including how variables were derived that were not included in the ISIMIP input data')

    def _get_verbose_field_name(self, field):
        fieldmeta = self._meta.get_field(field)
        ret = fieldmeta.verbose_name.title()
        if fieldmeta.help_text:
            ret = generate_helptext(fieldmeta.help_text, ret)
        return ret

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        return ('Input data sets used', [
                (vname('simulated_atmospheric_climate_data_sets'), ', '.join([x.pretty() for x in self.simulated_atmospheric_climate_data_sets.all()])),
                (vname('observed_atmospheric_climate_data_sets'), ', '.join([x.pretty() for x in self.observed_atmospheric_climate_data_sets.all()])),
                (vname('emissions_data_sets'), ', '.join([x.pretty() for x in self.emissions_data_sets.all()])),
                (vname('socio_economic_data_sets'), ', '.join([x.pretty() for x in self.socio_economic_data_sets.all()])),
                (vname('land_use_data_sets'), ', '.join([x.pretty() for x in self.land_use_data_sets.all()])),
                (vname('other_human_influences_data_sets'), ', '.join([x.pretty() for x in self.other_human_influences_data_sets.all()])),
                (vname('other_data_sets'), ', '.join([x.pretty() for x in self.other_data_sets.all()])),
                (vname('climate_variables'), ', '.join([x.as_span() for x in self.climate_variables.all()])),
                (vname('climate_variables_info'), self.climate_variables_info),
                (vname('additional_input_data_sets'), self.additional_input_data_sets),
                ])


class OtherInformation(models.Model):
    impact_model = models.OneToOneField(
        ImpactModel,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    exceptions_to_protocol = models.TextField(
        null=True, blank=True, default='', verbose_name='Exceptions',
        help_text='Any settings prescribed by the ISIMIP protocol that were overruled when runing the model'
    )
    YES_NO = ((True, 'Yes'), (False, 'No'))
    spin_up = models.BooleanField(
        verbose_name='Was a spin-up performed?',
        help_text="'No' indicates the simulations were run starting in the first reporting year 1971",
        choices=YES_NO,
        null=True, blank=True)
    spin_up_design = models.TextField(
        null=True, blank=True, default='', verbose_name='Spin-up design',
        help_text="Including the length of the spin up, the CO2 concentration used, and any deviations from the spin-up procedure defined in the protocol"
    )
    natural_vegetation_partition = models.TextField(
        null=True, blank=True, default='', help_text='How areas covered by different types of natural vegetation are partitioned'
    )
    natural_vegetation_dynamics = models.TextField(
        null=True, blank=True, default='',
        help_text='Description of how natural vegetation is simulated dynamically where relevant'
    )
    natural_vegetation_cover_dataset = models.TextField(
        null=True, blank=True, default='', help_text='Dataset used if natural vegetation cover is prescribed'
    )
    soil_layers = models.TextField(
        null=True, blank=True, default='', help_text=''
    )
    management = models.TextField(
        null=True, blank=True, default='',
        help_text='Please specify management in the general setup. Any sector specific management information is detailed in section 6. Sector-specific information.'
    )
    extreme_events = models.TextField(
        null=True, blank=True, default='', verbose_name='Key challenges',
        help_text='Key challenges for this model in reproducing impacts of extreme events such as pests, fire, water logging, frost damage.'
    )
    anything_else = models.TextField(
        verbose_name='Additional comments',
        null=True, blank=True, default='', help_text='Anything else necessary to reproduce and/or understand the simulation output'
    )

    def _get_verbose_field_name(self, field):
        fieldmeta = self._meta.get_field(field)
        ret = fieldmeta.verbose_name.title()
        if fieldmeta.help_text:
            ret = generate_helptext(fieldmeta.help_text, ret)
        return ret

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        return [
            ('Exceptions to Protocol', [
                (vname('exceptions_to_protocol'), self.exceptions_to_protocol),
            ]),
            ('Spin-up', [
                (vname('spin_up'), 'Yes' if self.spin_up is True else 'No' if self.spin_up is False else ''),
                (vname('spin_up_design'), self.spin_up_design if self.spin_up else ''),
            ]),
            ('Natural Vegetation', [
                (vname('natural_vegetation_partition'), self.natural_vegetation_partition),
                (vname('natural_vegetation_dynamics'), self.natural_vegetation_dynamics),
                (vname('natural_vegetation_cover_dataset'), self.natural_vegetation_cover_dataset),
                (vname('soil_layers'), self.soil_layers),
            ]),
            ('Management & Adaptation Measures', [
                (vname('management'), self.management),
            ]),
            ('Extreme Events & Disturbances', [
                (vname('extreme_events'), self.extreme_events),
                (vname('anything_else'), self.anything_else),
            ])
        ]


class BaseSector(models.Model):
    impact_model = models.OneToOneField(ImpactModel, on_delete=models.CASCADE)
    data = JSONField(blank=True, null=True, default=dict)

    class Meta:
        abstract = True

    def __str__(self):
        return '%s' % (self.impact_model)

    def _get_verbose_field_name(self, field):
        fieldmeta = self._meta.get_field(field)
        ret = fieldmeta.verbose_name.title()
        if fieldmeta.help_text:
            ret = generate_helptext(fieldmeta.help_text, ret)
        return ret

    def _get_verbose_field_name_question(self, field):
        fieldmeta = self._meta.get_field(field)
        ret = fieldmeta.verbose_name
        if fieldmeta.help_text:
            ret = generate_helptext(fieldmeta.help_text, ret)
        return ret

    def _get_generic_verbose_field_name(self, field):
        ret = field.name
        if field.help_text:
            ret = generate_helptext(field.help_text, ret)
        return ret

    def values_to_tuples(self):
        if not self.data:
            return []
        groups = []
        vname = self._get_generic_verbose_field_name
        for group in SectorInformationGroup.objects.filter(sector=self.impact_model.base_model.sector):
                fields = []
                for field in group.fields.all():
                    fields.append((vname(field), self.data.get(field.unique_identifier, '')))
                groups.append((group.name, fields))
        return groups


class GenericSector(BaseSector):
    def __str__(self):
        return '%s' % self.impact_model.base_model.sector

    class Meta:
        verbose_name = 'Generic sector'


class Agriculture(BaseSector):
    # Key input and Management, help_text="Provide a yes/no answer and a short description of how the process is included"
    crops = models.TextField(null=True, blank=True, default='', verbose_name='Crops')
    land_coverage = models.TextField(null=True, blank=True, default='', verbose_name='Land cover')
    planting_date_decision = models.TextField(null=True, blank=True, default='', verbose_name='Planting date decision')
    planting_density = models.TextField(null=True, blank=True, default='', verbose_name='Planting density')
    crop_cultivars = models.TextField(null=True, blank=True, default='', verbose_name='Crop cultivars')
    fertilizer_application = models.TextField(null=True, blank=True, default='', verbose_name='Fertilizer application')
    irrigation = models.TextField(null=True, blank=True, default='', verbose_name='Irrigation')
    crop_residue = models.TextField(null=True, blank=True, default='', verbose_name='Crop residue')
    initial_soil_water = models.TextField(null=True, blank=True, default='', verbose_name='Initial soil water')
    initial_soil_nitrate_and_ammonia = models.TextField(null=True, blank=True, default='', verbose_name='Initial soil nitrate and ammonia')
    initial_soil_C_and_OM = models.TextField(null=True, blank=True, default='', verbose_name='Initial soil C and OM')
    initial_crop_residue = models.TextField(null=True, blank=True, default='', verbose_name='Initial crop residue')
    # Key model processes, help_text="Please specify methods for model calibration and validation"
    lead_area_development = models.TextField(null=True, blank=True, default='', verbose_name='Leaf area development', help_text='Methods for model calibration and validation')
    light_interception = models.TextField(null=True, blank=True, default='', verbose_name='Light interception', help_text='Methods for model calibration and validation')
    light_utilization = models.TextField(null=True, blank=True, default='', verbose_name='Light utilization', help_text='Methods for model calibration and validation')
    yield_formation = models.TextField(null=True, blank=True, default='', verbose_name='Yield formation', help_text='Methods for model calibration and validation')
    crop_phenology = models.TextField(null=True, blank=True, default='', verbose_name='Crop phenology', help_text='Methods for model calibration and validation')
    root_distribution_over_depth = models.TextField(null=True, blank=True, default='', verbose_name='Root distribution over depth', help_text='Methods for model calibration and validation')
    stresses_involved = models.TextField(null=True, blank=True, default='', verbose_name='Stresses involved', help_text='Methods for model calibration and validation')
    type_of_water_stress = models.TextField(null=True, blank=True, default='', verbose_name='Type of water stress', help_text='Methods for model calibration and validation')
    type_of_heat_stress = models.TextField(null=True, blank=True, default='', verbose_name='Type of heat stress', help_text='Methods for model calibration and validation')
    water_dynamics = models.TextField(null=True, blank=True, default='', verbose_name='Water dynamics', help_text='Methods for model calibration and validation')
    evapo_transpiration = models.TextField(null=True, blank=True, default='', verbose_name='Evapo-transpiration', help_text='Methods for model calibration and validation')
    soil_CN_modeling = models.TextField(null=True, blank=True, default='', verbose_name='Soil CN modeling', help_text='Methods for model calibration and validation')
    co2_effects = models.TextField(null=True, blank=True, default='', verbose_name='CO2 Effects', help_text='Methods for model calibration and validation')
    # Methods for model calibration and validation , help_text="Please specify methods for model calibration and validation"
    parameters_number_and_description = models.TextField(null=True, blank=True, default='', verbose_name='Parameters, number and description')
    calibrated_values = models.TextField(null=True, blank=True, default='', verbose_name='Calibrated values')
    output_variable_and_dataset = models.TextField(null=True, blank=True, default='', verbose_name='Output variable and dataset for calibration validation')
    spatial_scale_of_calibration_validation = models.TextField(null=True, blank=True, default='', verbose_name='Spatial scale of calibration/validation')
    temporal_scale_of_calibration_validation = models.TextField(null=True, blank=True, default='', verbose_name='Temporal scale of calibration/validation')
    criteria_for_evaluation = models.TextField(null=True, blank=True, default='', verbose_name='Criteria for evaluation (validation)')

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        generic = super(Agriculture, self).values_to_tuples()
        return [
            ('Key input and Management', [
                (vname('crops'), self.crops),
                (vname('land_coverage'), self.land_coverage),
                (vname('planting_date_decision'), self.planting_date_decision),
                (vname('planting_density'), self.planting_density),
                (vname('crop_cultivars'), self.crop_cultivars),
                (vname('fertilizer_application'), self.fertilizer_application),
                (vname('irrigation'), self.irrigation),
                (vname('crop_residue'), self.crop_residue),
                (vname('initial_soil_water'), self.initial_soil_water),
                (vname('initial_soil_nitrate_and_ammonia'), self.initial_soil_nitrate_and_ammonia),
                (vname('initial_soil_C_and_OM'), self.initial_soil_C_and_OM),
                (vname('initial_crop_residue'), self.initial_crop_residue)
            ]),
            ('Key model processes', [
                (vname('lead_area_development'), self.lead_area_development),
                (vname('light_interception'), self.light_interception),
                (vname('light_utilization'), self.light_utilization),
                (vname('yield_formation'), self.yield_formation),
                (vname('crop_phenology'), self.crop_phenology),
                (vname('root_distribution_over_depth'), self.root_distribution_over_depth),
                (vname('stresses_involved'), self.stresses_involved),
                (vname('type_of_water_stress'), self.type_of_water_stress),
                (vname('type_of_heat_stress'), self.type_of_heat_stress),
                (vname('water_dynamics'), self.water_dynamics),
                (vname('evapo_transpiration'), self.evapo_transpiration),
                (vname('soil_CN_modeling'), self.soil_CN_modeling),
                (vname('co2_effects'), self.co2_effects),
            ]),
            ('Methods for model calibration and validation', [
                (vname('parameters_number_and_description'), self.parameters_number_and_description),
                (vname('calibrated_values'), self.calibrated_values),
                (vname('output_variable_and_dataset'), self.output_variable_and_dataset),
                (vname('spatial_scale_of_calibration_validation'), self.spatial_scale_of_calibration_validation),
                (vname('temporal_scale_of_calibration_validation'), self.temporal_scale_of_calibration_validation),
                (vname('criteria_for_evaluation'), self.criteria_for_evaluation)
            ])
        ] + generic


class BiomesForests(BaseSector):
    # technological_progress = models.TextField(null=True, blank=True, default='')
    output = models.TextField(
        null=True, blank=True, default='', verbose_name='Output format',
        help_text='Is output (e.g. PFT cover) written out per grid-cell area or per land and water area within a grid cell, or land only?'
    )
    output_per_pft = models.TextField(
        null=True, blank=True, default='', verbose_name='Output per PFT?',
        help_text='Is output per PFT per unit area of that PFT, i.e. requiring weighting by the fractional coverage of each PFT to get the gridbox average?'
    )
    considerations = models.TextField(
        null=True, blank=True, default='',
        help_text='Things to consider, when calculating basic variables such as GPP, NPP, RA, RH from the model.'
    )
    # key model processes , help_text="Please provide yes/no and a short description how the process is included"
    dynamic_vegetation = models.TextField(null=True, blank=True, default='')
    nitrogen_limitation = models.TextField(null=True, blank=True, default='')
    co2_effects = models.TextField(null=True, blank=True, default='', verbose_name='CO2 effects')
    light_interception = models.TextField(null=True, blank=True, default='')
    light_utilization = models.TextField(null=True, blank=True, default='', help_text="photosynthesis, RUE-approach?")
    phenology = models.TextField(null=True, blank=True, default='')
    water_stress = models.TextField(null=True, blank=True, default='')
    heat_stress = models.TextField(null=True, blank=True, default='')
    evapotranspiration_approach = models.TextField(verbose_name='Evapo-transpiration approach', null=True, blank=True, default='')
    rooting_depth_differences = models.TextField(verbose_name='Differences in rooting depth', null=True, blank=True, default='',
                                                 help_text="Including how it changes")
    root_distribution = models.TextField(verbose_name='Root distribution over depth', null=True, blank=True, default='')
    permafrost = models.TextField(null=True, blank=True, default='')
    closed_energy_balance = models.TextField(null=True, blank=True, default='')
    soil_moisture_surface_temperature_coupling = models.TextField(
        null=True, blank=True, default='', verbose_name='Coupling/feedback between soil moisture and surface temperature')
    latent_heat = models.TextField(null=True, blank=True, default='')
    sensible_heat = models.TextField(null=True, blank=True, default='')
    # causes of mortality in vegetation models , help_text="Describe briefly how the process is described in this model and in which way it is climate dependent."
    mortality_age = models.TextField(verbose_name='Age/Senescence', null=True, blank=True, default='')
    mortality_fire = models.TextField(verbose_name='Fire', null=True, blank=True, default='')
    mortality_drought = models.TextField(verbose_name='Drought', null=True, blank=True, default='')
    mortality_insects = models.TextField(verbose_name='Insects', null=True, blank=True, default='')
    mortality_storm = models.TextField(verbose_name='Storm', null=True, blank=True, default='')
    mortality_stochastic_random_disturbance = models.TextField(verbose_name='Stochastic random disturbance', null=True, blank=True, default='')
    mortality_other = models.TextField(verbose_name='Other', null=True, blank=True, default='')
    mortality_remarks = models.TextField(verbose_name='Remarks', null=True, blank=True, default='')
    # NBP components , help_text="Indicate whether the model includes the processes, and how the model accounts for the fluxes, i.e.what is the fate of the biomass? E.g.directly to atmsphere or let it go to other pool"
    nbp_fire = models.TextField(null=True, blank=True, default='', verbose_name='Fire', help_text='Indicate whether the model includes fire, and how the model accounts for the fluxes, i.e. what is the fate of the biomass? E.g. directly to atmsphere or let it go to other pool')
    nbp_landuse_change = models.TextField(null=True, blank=True, default='', verbose_name='Land-use change',
                                          help_text="Indicate whether the model includes land-use change (e.g. deforestation harvest and otherland-use changes), and how the model accounts for the fluxes, i.e. what is the fate of the biomass? e.g. directly to atmsphere or let it go to other pool")
    nbp_harvest = models.TextField(
        null=True, blank=True, default='', verbose_name='Harvest',
        help_text="Indicate whether the model includes harvest, and how the model accounts for the fluxes, i.e. what is the fate of the biomass? E.g. directly to atmsphere or let it go to other pool. 1: crops, 2: harvest from forest management, 3: harvest from grassland management."
    )
    nbp_other = models.TextField(null=True, blank=True, default='', verbose_name='Other processes')
    nbp_comments = models.TextField(null=True, blank=True, default='', verbose_name='Comments')
    # Species / Plant Functional Types (PFTs)
    list_of_pfts = models.TextField(
        null=True, blank=True, default='', verbose_name='List of species / PFTs',
        help_text="Provide a list of PFTs using the folllowing format: [pft1_long_name] ([pft1_short_name]); [pft2_long_name] ([pft2_short_name]). Include long name in brackets if no short name is available."
    )
    pfts_comments = models.TextField(null=True, blank=True, default='', verbose_name='Comments')

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        generic = super(BiomesForests, self).values_to_tuples()
        return [
            ('Key model processes', [
                (vname('dynamic_vegetation'), self.dynamic_vegetation),
                (vname('nitrogen_limitation'), self.nitrogen_limitation),
                (vname('co2_effects'), self.co2_effects),
                (vname('light_interception'), self.light_interception),
                (vname('light_utilization'), self.light_utilization),
                (vname('phenology'), self.phenology),
                (vname('water_stress'), self.water_stress),
                (vname('heat_stress'), self.heat_stress),
                (vname('evapotranspiration_approach'), self.evapotranspiration_approach),
                (vname('rooting_depth_differences'), self.rooting_depth_differences),
                (vname('root_distribution'), self.root_distribution),
                (vname('permafrost'), self.permafrost),
                (vname('closed_energy_balance'), self.closed_energy_balance),
                (vname('soil_moisture_surface_temperature_coupling'), self.soil_moisture_surface_temperature_coupling),
                (vname('latent_heat'), self.latent_heat),
                (vname('sensible_heat'), self.sensible_heat),
            ]),
            ('Causes of mortality in vegetation models', [
                (vname('mortality_age'), self.mortality_age),
                (vname('mortality_fire'), self.mortality_fire),
                (vname('mortality_drought'), self.mortality_drought),
                (vname('mortality_insects'), self.mortality_insects),
                (vname('mortality_storm'), self.mortality_storm),
                (vname('mortality_stochastic_random_disturbance'), self.mortality_stochastic_random_disturbance),
                (vname('mortality_other'), self.mortality_other),
                (vname('mortality_remarks'), self.mortality_remarks),
            ]),
            ('NBP components', [
                (vname('nbp_fire'), self.nbp_fire),
                (vname('nbp_landuse_change'), self.nbp_landuse_change),
                (vname('nbp_harvest'), self.nbp_harvest),
                (vname('nbp_other'), self.nbp_other),
                (vname('nbp_comments'), self.nbp_comments),
            ]),
            ('Species / Plant Functional Types (PFTs)', [
                (vname('list_of_pfts'), self.list_of_pfts),
                (vname('pfts_comments'), self.pfts_comments),
            ]),
            ('Model output specifications', [
                (vname('output'), self.output),
                (vname('output_per_pft'), self.output_per_pft),
                (vname('considerations'), self.considerations),
            ]),
        ] + generic

    class Meta:
        abstract = True


class Biomes(BiomesForests):
    # key model processes
    compute_soil_carbon = models.TextField(null=True, blank=True, default='', verbose_name='How do you compute soil organic carbon during land use (do you mix the previous PFT SOC into agricultural SOC)?')
    seperate_soil_carbon = models.TextField(null=True, blank=True, default='', verbose_name='Do you separate soil organic carbon in pasture from natural grass?')
    harvest_npp_crops = models.TextField(null=True, blank=True, default='', verbose_name='Do you harvest NPP of crops? Do you including grazing? How does harvested NPP decay?')
    treat_biofuel_npp = models.TextField(null=True, blank=True, default='', verbose_name='How do you to treat biofuel NPP and biofuel harvest?')
    npp_litter_output = models.TextField(null=True, blank=True, default='', verbose_name='Does non-harvested crop NPP go to litter in your output?')
    # model setup
    simulate_bioenergy = models.TextField(null=True, blank=True, default='', verbose_name='How do you simulate bioenergy? I.e. What PFT do you simulate on bioenergy land?')
    transition_cropland = models.TextField(null=True, blank=True, default='', verbose_name='How do you simulate the transition from cropland to bioenergy?')
    simulate_pasture = models.TextField(null=True, blank=True, default='', verbose_name='How do you simulate pasture (which PFT)?')

    class Meta:
        verbose_name_plural = 'Biomes'
        verbose_name = 'Biomes'

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        generic = super(BiomesForests, self).values_to_tuples()
        return [
            ('Model set-up specifications', [
                (vname('simulate_bioenergy'), self.simulate_bioenergy),
                (vname('transition_cropland'), self.transition_cropland),
                (vname('simulate_pasture'), self.simulate_pasture),
            ]),
            ('Key model processes', [
                (vname('dynamic_vegetation'), self.dynamic_vegetation),
                (vname('nitrogen_limitation'), self.nitrogen_limitation),
                (vname('co2_effects'), self.co2_effects),
                (vname('light_interception'), self.light_interception),
                (vname('light_utilization'), self.light_utilization),
                (vname('phenology'), self.phenology),
                (vname('water_stress'), self.water_stress),
                (vname('heat_stress'), self.heat_stress),
                (vname('evapotranspiration_approach'), self.evapotranspiration_approach),
                (vname('rooting_depth_differences'), self.rooting_depth_differences),
                (vname('root_distribution'), self.root_distribution),
                (vname('permafrost'), self.permafrost),
                (vname('closed_energy_balance'), self.closed_energy_balance),
                (vname('soil_moisture_surface_temperature_coupling'), self.soil_moisture_surface_temperature_coupling),
                (vname('latent_heat'), self.latent_heat),
                (vname('sensible_heat'), self.sensible_heat),
                (vname('compute_soil_carbon'), self.compute_soil_carbon),
                (vname('seperate_soil_carbon'), self.seperate_soil_carbon),
                (vname('harvest_npp_crops'), self.harvest_npp_crops),
                (vname('treat_biofuel_npp'), self.treat_biofuel_npp),
                (vname('npp_litter_output'), self.npp_litter_output),
            ]),
            ('Causes of mortality in vegetation models', [
                (vname('mortality_age'), self.mortality_age),
                (vname('mortality_fire'), self.mortality_fire),
                (vname('mortality_drought'), self.mortality_drought),
                (vname('mortality_insects'), self.mortality_insects),
                (vname('mortality_storm'), self.mortality_storm),
                (vname('mortality_stochastic_random_disturbance'), self.mortality_stochastic_random_disturbance),
                (vname('mortality_other'), self.mortality_other),
                (vname('mortality_remarks'), self.mortality_remarks),
            ]),
            ('NBP components', [
                (vname('nbp_fire'), self.nbp_fire),
                (vname('nbp_landuse_change'), self.nbp_landuse_change),
                (vname('nbp_harvest'), self.nbp_harvest),
                (vname('nbp_other'), self.nbp_other),
                (vname('nbp_comments'), self.nbp_comments),
            ]),
            ('Species / Plant Functional Types (PFTs)', [
                (vname('list_of_pfts'), self.list_of_pfts),
                (vname('pfts_comments'), self.pfts_comments),
            ]),
            ('Model output specifications', [
                (vname('output'), self.output),
                (vname('output_per_pft'), self.output_per_pft),
                (vname('considerations'), self.considerations),
            ]),
        ] + generic


class Fire(BaseSector):
    # Input data sets used
    input_datasets_used = models.TextField(null=True, blank=True, default='', verbose_name='What input datasets are used in the fire model and what are they used for?')
    time_step_fire_model = models.TextField(null=True, blank=True, default='', verbose_name='What is the time step of the fire model?')
    time_step_exchange = models.TextField(null=True, blank=True, default='', verbose_name='What is the time step of the exchange between fire and vegetation model? e.g. are carbon pools and cover fractions updated every day?')
    # Burnt Area
    main_components_burnt_area = models.TextField(null=True, blank=True, default='', verbose_name='What are the main components of burned area computation?')
    # Ignition
    sources_of_ignition = models.TextField(null=True, blank=True, default='', verbose_name='Which sources of ignition are included?')
    fire_ignition_implemented = models.TextField(null=True, blank=True, default='', verbose_name='Is fire ignition implemented as a random process?')
    natural_ignition_implemented = models.TextField(null=True, blank=True, default='', verbose_name='How are natural ignitions implemented? Which data is used and how is it scaled?')
    human_ignition = models.TextField(null=True, blank=True, default='', verbose_name='Is human influence on fire ignition and/or suppression included? How?')
    human_ignition_conditions = models.TextField(null=True, blank=True, default='', verbose_name='If human ignitions are included for which conditions are the ignitions highest/lowest?')

    # Spread and duration
    how_does_fire_spread = models.TextField(null=True, blank=True, default='', verbose_name='How does fire spread?')
    fire_duration_computed = models.TextField(null=True, blank=True, default='', verbose_name='How is fire duration computed?')
    # Fuel load and combustion
    model_compute_fuel_load = models.TextField(null=True, blank=True, default='', verbose_name='How does the model compute fuel load?')
    list_of_fuel_classes = models.TextField(null=True, blank=True, default='', verbose_name='List of fuel classes (full names and abbreviations)')
    fuel_moisture_linked = models.TextField(null=True, blank=True, default='', verbose_name='Is fuel moisture linked to soil moisture/air humidity/precip?')
    carbon_pools_combusted = models.TextField(null=True, blank=True, default='', verbose_name='Which carbon pools are combusted?')
    combustion_completeness = models.TextField(null=True, blank=True, default='', verbose_name='Is the combustion completeness constant or depends on what (fuel type, moisture?)')
    # Landcover
    min_max_burned_area_grid = models.TextField(null=True, blank=True, default='', verbose_name='What is the minimum/maximum burned area fraction at grid cell level? Over which time period? ')
    land_cover_classes_allowed = models.TextField(null=True, blank=True, default='', verbose_name='Land-cover classes allowed to burn')
    burned_area_computed_separately = models.TextField(null=True, blank=True, default='', verbose_name='Is burned area computed separately for each PFT? If not how is burned area separated into the PFT-burned area? ')
    peatland_fires_included = models.TextField(null=True, blank=True, default='', verbose_name='Are peatland fires included?')
    deforestation_or_clearing_included = models.TextField(null=True, blank=True, default='', verbose_name='Are deforestation or land clearing fires included?')
    pastures_represented = models.TextField(null=True, blank=True, default='', verbose_name='How are pastures represented?')
    cropland_burn_differ = models.TextField(null=True, blank=True, default='', verbose_name='If croplands burn, does the fire model differ for this PFT? If yes please describe.')
    pasture_burn_differ = models.TextField(null=True, blank=True, default='', verbose_name='If pastures burn, does the fire model differ for his PFT? If yes, please describe')
    # Fire mortality
    vegetation_fire_mortality = models.TextField(null=True, blank=True, default='', verbose_name='vegetation fire mortality: is it constant/constant per pft/depends on (for instance fire intensity, bark thickness, veg height)')

    class Meta:
        verbose_name_plural = 'Fires'
        verbose_name = 'Fire'

    def values_to_tuples(self):
        vname = self._get_verbose_field_name_question
        generic = super(Fire, self).values_to_tuples()
        return [
            ('Fire-specific input data sets', [
                (vname('input_datasets_used'), self.input_datasets_used),
                (vname('time_step_fire_model'), self.time_step_fire_model),
                (vname('time_step_exchange'), self.time_step_exchange),
            ]),
            ('Burnt Area', [
                (vname('main_components_burnt_area'), self.main_components_burnt_area),
            ]),
            ('Ignition', [
                (vname('sources_of_ignition'), self.sources_of_ignition),
                (vname('fire_ignition_implemented'), self.fire_ignition_implemented),
                (vname('natural_ignition_implemented'), self.natural_ignition_implemented),
                (vname('human_ignition'), self.human_ignition),
                (vname('human_ignition_conditions'), self.human_ignition_conditions),
            ]),
            ('Spread and duration', [
                (vname('how_does_fire_spread'), self.how_does_fire_spread),
                (vname('fire_duration_computed'), self.fire_duration_computed),
            ]),
            ('Fuel load and combustion', [
                (vname('model_compute_fuel_load'), self.model_compute_fuel_load),
                (vname('list_of_fuel_classes'), self.list_of_fuel_classes),
                (vname('fuel_moisture_linked'), self.fuel_moisture_linked),
                (vname('carbon_pools_combusted'), self.carbon_pools_combusted),
                (vname('combustion_completeness'), self.combustion_completeness),
            ]),
            ('Landcover', [
                (vname('min_max_burned_area_grid'), self.min_max_burned_area_grid),
                (vname('land_cover_classes_allowed'), self.land_cover_classes_allowed),
                (vname('burned_area_computed_separately'), self.burned_area_computed_separately),
                (vname('peatland_fires_included'), self.peatland_fires_included),
                (vname('deforestation_or_clearing_included'), self.deforestation_or_clearing_included),
                (vname('pastures_represented'), self.pastures_represented),
                (vname('cropland_burn_differ'), self.cropland_burn_differ),
                (vname('pasture_burn_differ'), self.pasture_burn_differ),
            ]),
            ('Fire mortality', [
                (vname('vegetation_fire_mortality'), self.vegetation_fire_mortality),
            ]),
        ] + generic


class Forests(BiomesForests):
    # Forest Model Set-up Specifications
    initialize_model = models.TextField(null=True, blank=True, default='', verbose_name='How did you initialize your model, e.g. using Individual tree dbh and height or stand basal area? How do you initialize soil conditions?')
    data_profound_db = models.TextField(null=True, blank=True, default='', verbose_name='Which data from PROFOUND DB did you use for initialisation (name of variable, which year)? From stand data or from individual tree data?')
    management_implementation = models.TextField(null=True, blank=True, default='', verbose_name='How is management implemented? E.g. do you harvest biomass/basal area proportions or by tree numbers or dimensions (target dbh)?')
    harvesting_simulated = models.TextField(null=True, blank=True, default='', verbose_name='When is harvesting simulated by your model (start/middle/end of the year, i.e., before or after the growing season)?')
    regenerate = models.TextField(null=True, blank=True, default='', verbose_name='How do you regenerate? Do you plant seedlings one year after harvest or several years of gap and then plant larger saplings?')
    unmanaged_simulations = models.TextField(null=True, blank=True, default='', verbose_name='How are the unmanaged simulations designed? Is there some kind of regrowth/regeneration or are the existing trees just growing older and older?')
    noco2_scenario = models.TextField(null=True, blank=True, default='', verbose_name='How are models implementing the noco2 scenario? Please confirm that co2 is follwing the historical trend (based on PROFUND DB) until 2000 (for ISIMIPFT) or 2005 (for ISIMIP2b) and then fixed at 2000 or 2005 value respectively?')
    leap_years = models.TextField(null=True, blank=True, default='', verbose_name='Does your model consider leap-years or a 365 calendar only? Or any other calendar?')
    simulate_minor_tree = models.TextField(null=True, blank=True, default='', verbose_name='In hyytiälä and kroof, how did you simulate the "minor tree species"? e.g. in hyytiälä did you simulate only pine trees and removed the spruce trees or did you interpret spruce basal area as being pine basal area?')
    nitrogen_simulation = models.TextField(null=True, blank=True, default='', verbose_name='How did you simulate nitrogen deposition from 2005 onwards in the 2b picontrol run? Please confirm you kept them constant at 2005-levels?')
    soil_depth = models.TextField(null=True, blank=True, default='', verbose_name='What is the soil depth you assumed for each site and how many soil layers (including their depths) do you assume in each site? Please upload a list of the soil depth and soil layers your model assumes for each site as an attachment (Section 7).')
    stochastic_element = models.TextField(null=True, blank=True, default='', verbose_name='Is there any stochastic element in your model (e.g. in the management or mortality submodel) that will lead to slightly different results if the model is re-run, even though all drivers etc. remain the same?')
    minimum_diameter_tree = models.TextField(null=True, blank=True, default='', verbose_name='What is the minimum diameter at which a „tree is considered a tree“? and is there a similar threshold for the minimum harvestable diameter?')
    model_historically_calibrated = models.TextField(null=True, blank=True, default='', verbose_name='Has your model been "historically calibrated" to any of the sites you simulated? e.g. has the site been used for model testing during model development?')
    upload_parameter_list = models.TextField(null=True, blank=True, default='', verbose_name='Please upload a list of your parameters as an attachment (Section 7). The list should include species-specific parameters and other parameters not depending on initialization data including the following information: short name, long name, short explanation, unit, value, see here for an example (http://www.pik-potsdam.de/4c/web_4c/theory/parameter_table_0514.pdf)')
    # key model processes , help_text="Please provide yes/no and a short description how the process is included"
    assimilation = models.TextField(null=True, blank=True, default='', verbose_name='Assimilation')
    respiration = models.TextField(null=True, blank=True, default='', verbose_name='Respiration')
    carbon_allocation = models.TextField(null=True, blank=True, default='', verbose_name='Carbon allocation')
    regeneration_planting = models.TextField(null=True, blank=True, default='', verbose_name='Regeneration/planting')
    soil_water_balance = models.TextField(null=True, blank=True, default='', verbose_name='Soil water balance')
    carbon_nitrogen_balance = models.TextField(null=True, blank=True, default='', verbose_name='Carbon/Nitrogen balance')
    feedbacks_considered = models.TextField(null=True, blank=True, default='', verbose_name='Are feedbacks considered that reflect the influence of changing carbon state variables on the other system components and driving data (i.e. Growth (leaf area), light, temperature, water availability, nutrient availability)?')
    # Forest Model Output Specifications
    initial_state = models.TextField(null=True, blank=True, default='', verbose_name='Do you provide the initial state in your simulation outputs (i.e., at year 0; before the simulation starts)?')
    total_calculation = models.TextField(null=True, blank=True, default='', verbose_name='When you report a variable as "xxx-total" does it equal the (sum of) "xxx-species" value(s)? or are there confounding factors such as ground/herbaceous vegetation contributing to the "total" in your model?')
    output_dbh_class = models.TextField(null=True, blank=True, default='', verbose_name='Did you report any output per dbh-class? if yes, which variables?')


    class Meta:
        verbose_name_plural = 'Forests'
        verbose_name = 'Forests'

    def values_to_tuples(self):
        vname = self._get_verbose_field_name_question
        generic = super(BiomesForests, self).values_to_tuples()
        return [
            ('Model set-up specifications', [
                (vname('initialize_model'), self.initialize_model),
                (vname('data_profound_db'), self.data_profound_db),
                (vname('management_implementation'), self.management_implementation),
                (vname('harvesting_simulated'), self.harvesting_simulated),
                (vname('regenerate'), self.regenerate),
                (vname('unmanaged_simulations'), self.unmanaged_simulations),
                (vname('noco2_scenario'), self.noco2_scenario),
                (vname('leap_years'), self.leap_years),
                (vname('simulate_minor_tree'), self.simulate_minor_tree),
                (vname('nitrogen_simulation'), self.nitrogen_simulation),
                (vname('soil_depth'), self.soil_depth),
                (vname('stochastic_element'), self.stochastic_element),
                (vname('minimum_diameter_tree'), self.minimum_diameter_tree),
                (vname('model_historically_calibrated'), self.model_historically_calibrated),
                (vname('upload_parameter_list'), self.upload_parameter_list),
            ]),
            ('Key model processes', [
                (vname('dynamic_vegetation'), self.dynamic_vegetation),
                (vname('nitrogen_limitation'), self.nitrogen_limitation),
                (vname('co2_effects'), self.co2_effects),
                (vname('light_interception'), self.light_interception),
                (vname('light_utilization'), self.light_utilization),
                (vname('phenology'), self.phenology),
                (vname('water_stress'), self.water_stress),
                (vname('heat_stress'), self.heat_stress),
                (vname('evapotranspiration_approach'), self.evapotranspiration_approach),
                (vname('rooting_depth_differences'), self.rooting_depth_differences),
                (vname('root_distribution'), self.root_distribution),
                (vname('permafrost'), self.permafrost),
                (vname('closed_energy_balance'), self.closed_energy_balance),
                (vname('soil_moisture_surface_temperature_coupling'), self.soil_moisture_surface_temperature_coupling),
                (vname('latent_heat'), self.latent_heat),
                (vname('sensible_heat'), self.sensible_heat),
                (vname('assimilation'), self.assimilation),
                (vname('respiration'), self.respiration),
                (vname('carbon_allocation'), self.carbon_allocation),
                (vname('regeneration_planting'), self.regeneration_planting),
                (vname('soil_water_balance'), self.soil_water_balance),
                (vname('carbon_nitrogen_balance'), self.carbon_nitrogen_balance),
                (vname('feedbacks_considered'), self.feedbacks_considered),
            ]),
            ('Causes of mortality in vegetation models', [
                (vname('mortality_age'), self.mortality_age),
                (vname('mortality_fire'), self.mortality_fire),
                (vname('mortality_drought'), self.mortality_drought),
                (vname('mortality_insects'), self.mortality_insects),
                (vname('mortality_storm'), self.mortality_storm),
                (vname('mortality_stochastic_random_disturbance'), self.mortality_stochastic_random_disturbance),
                (vname('mortality_other'), self.mortality_other),
                (vname('mortality_remarks'), self.mortality_remarks),
            ]),
            ('NBP components', [
                (vname('nbp_fire'), self.nbp_fire),
                (vname('nbp_landuse_change'), self.nbp_landuse_change),
                (vname('nbp_harvest'), self.nbp_harvest),
                (vname('nbp_other'), self.nbp_other),
                (vname('nbp_comments'), self.nbp_comments),
            ]),
            ('Species / Plant Functional Types (PFTs)', [
                (vname('list_of_pfts'), self.list_of_pfts),
                (vname('pfts_comments'), self.pfts_comments),
            ]),
            ('Model output specifications', [
                (vname('initial_state'), self.initial_state),
                (vname('output'), self.output),
                (vname('output_per_pft'), self.output_per_pft),
                (vname('total_calculation'), self.total_calculation),
                (vname('output_dbh_class'), self.output_dbh_class),
                (vname('considerations'), self.considerations),
            ]),
        ] + generic


class Energy(BaseSector):
    # Model & Method Characteristics
    model_type = models.TextField(null=True, blank=True, default='', verbose_name='Model type')
    temporal_extent = models.TextField(null=True, blank=True, default='', verbose_name='Temporal extent')
    temporal_resolution = models.TextField(null=True, blank=True, default='', verbose_name='Temporal resolution')
    data_format_for_input = models.TextField(null=True, blank=True, default='', verbose_name='Data format for input')
    # Impact Types
    impact_types_energy_demand = models.TextField(null=True, blank=True, default='', verbose_name='Energy demand (heating & cooling)')
    impact_types_temperature_effects_on_thermal_power = models.TextField(null=True, blank=True, default='', verbose_name='Temperature effects on thermal power')
    impact_types_weather_effects_on_renewables = models.TextField(null=True, blank=True, default='', verbose_name='Weather effects on renewables')
    impact_types_water_scarcity_impacts = models.TextField(null=True, blank=True, default='', verbose_name='Water scarcity impacts')
    impact_types_other = models.TextField(null=True, blank=True, default='', verbose_name='Other (agriculture, infrastructure, adaptation)')
    # Output
    output_energy_demand = models.TextField(null=True, blank=True, default='', verbose_name='Energy demand (heating & cooling)')
    output_energy_supply = models.TextField(null=True, blank=True, default='', verbose_name='Energy supply')
    output_water_scarcity = models.TextField(null=True, blank=True, default='', verbose_name='Water scarcity')
    output_economics = models.TextField(null=True, blank=True, default='', verbose_name='Economics')
    output_other = models.TextField(null=True, blank=True, default='', verbose_name='Other (agriculture, infrastructure, adaptation)')
    # Further Information
    variables_not_directly_from_GCMs = models.TextField(null=True, blank=True, default='', verbose_name='Variables not directly from GCMs', help_text='How are these calculated (including equations)?')
    response_function_of_energy_demand_to_HDD_CDD = models.TextField(null=True, blank=True, default='', verbose_name='Response function of energy demand to HDD/CDD', help_text='Including equations where appropriate')
    factor_definition_and_calculation = models.TextField(null=True, blank=True, default='', verbose_name='Definition and calculation of variable potential and load factor', help_text='Are these endogenous or exogenous to the model?')
    biomass_types = models.TextField(null=True, blank=True, default='', verbose_name='Biomass types', help_text='1st generation, 2nd generation, residues...')
    maximum_potential_assumption = models.TextField(null=True, blank=True, default='', verbose_name='Maximum potential assumption', help_text='Which information source is used?')
    bioenergy_supply_costs = models.TextField(null=True, blank=True, default='', verbose_name='Bioenergy supply costs', help_text='Include information on the functional forms and the data sources for deriving the supply curves')
    socioeconomic_input = models.TextField(null=True, blank=True, default='', verbose_name='Socio-economic input', help_text='Are SSP storylines implemented, or just GDP and population scenarios?')

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        generic = super(Energy, self).values_to_tuples()
        return [
            ('Model & method characteristics', [
                (vname('model_type'), self.model_type),
                (vname('temporal_extent'), self.temporal_extent),
                (vname('temporal_resolution'), self.temporal_resolution),
                (vname('data_format_for_input'), self.data_format_for_input),
            ]),
            ('Impact Types', [

                (vname('impact_types_energy_demand'), self.impact_types_energy_demand),
                (vname('impact_types_temperature_effects_on_thermal_power'), self.impact_types_temperature_effects_on_thermal_power),
                (vname('impact_types_weather_effects_on_renewables'), self.impact_types_weather_effects_on_renewables),
                (vname('impact_types_water_scarcity_impacts'), self.impact_types_water_scarcity_impacts),
                (vname('impact_types_other'), self.impact_types_other),
            ]),
            ('Output', [
                (vname('output_energy_demand'), self.output_energy_demand),
                (vname('output_energy_supply'), self.output_energy_supply),
                (vname('output_water_scarcity'), self.output_water_scarcity),
                (vname('output_economics'), self.output_economics),
                (vname('output_other'), self.output_other),
            ]),
            ('Further Information', [
                (vname('variables_not_directly_from_GCMs'), self.variables_not_directly_from_GCMs),
                (vname('response_function_of_energy_demand_to_HDD_CDD'), self.response_function_of_energy_demand_to_HDD_CDD),
                (vname('factor_definition_and_calculation'), self.factor_definition_and_calculation),
                (vname('biomass_types'), self.biomass_types),
                (vname('maximum_potential_assumption'), self.maximum_potential_assumption),
                (vname('bioenergy_supply_costs'), self.bioenergy_supply_costs),
                (vname('socioeconomic_input'), self.socioeconomic_input),
            ])
        ] + generic


class MarineEcosystems(BaseSector):
    defining_features = models.TextField(null=True, blank=True, default='', verbose_name='Defining features')
    spatial_scale = models.TextField(null=True, blank=True, default='', verbose_name='Spatial scale')
    spatial_resolution = models.TextField(null=True, blank=True, default='', verbose_name='Spatial resolution')
    temporal_scale = models.TextField(null=True, blank=True, default='', verbose_name='Temporal scale')
    temporal_resolution = models.TextField(null=True, blank=True, default='', verbose_name='Temporal resolution')
    taxonomic_scope = models.TextField(null=True, blank=True, default='', verbose_name='Taxonomic scope')
    vertical_resolution = models.TextField(null=True, blank=True, default='', verbose_name='Vertical resolution')
    spatial_dispersal_included = models.TextField(null=True, blank=True, default='', verbose_name='Spatial dispersal included')
    fishbase_used_for_mass_length_conversion = models.TextField(
        null=True, blank=True, default='', verbose_name='Is FishBase used for mass-length conversion?')
    simulated_ocean_climate_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Simulated ocean climate data sets used",
                                                               help_text="The observed ocean climate data sets used in this simulation round", related_name="%(app_label)s_%(class)s_simulated")
    observed_ocean_climate_data_sets = models.ManyToManyField(InputData, blank=True, verbose_name="Observed ocean climate data sets used",
                                                              help_text="The observed ocean climate data sets used in this simulation round", related_name="%(app_label)s_%(class)s_observed")

    class Meta:
        abstract = True

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        generic = super(MarineEcosystems, self).values_to_tuples()
        return [
            ('Information specific to marine ecosystems & fisheries', [
                (vname('defining_features'), self.defining_features),
                (vname('spatial_scale'), self.spatial_scale),
                (vname('spatial_resolution'), self.spatial_resolution),
                (vname('temporal_scale'), self.temporal_scale),
                (vname('temporal_resolution'), self.temporal_resolution),
                (vname('taxonomic_scope'), self.taxonomic_scope),
                (vname('vertical_resolution'), self.vertical_resolution),
                (vname('spatial_dispersal_included'), self.spatial_dispersal_included),
                (vname('fishbase_used_for_mass_length_conversion'), self.fishbase_used_for_mass_length_conversion),
                (vname('simulated_ocean_climate_data_sets'), ', '.join([x.pretty() for x in self.simulated_ocean_climate_data_sets.all()])),
                (vname('observed_ocean_climate_data_sets'), ', '.join([x.pretty() for x in self.observed_ocean_climate_data_sets.all()])),
            ])
        ] + generic


class MarineEcosystemsGlobal(MarineEcosystems):
    class Meta:
        verbose_name = 'Marine Ecosystems and Fisheries (global)'
        verbose_name_plural = 'Marine Ecosystems and Fisheries (global)'


class MarineEcosystemsRegional(MarineEcosystems):
    class Meta:
        verbose_name = 'Marine Ecosystems and Fisheries (regional)'
        verbose_name_plural = 'Marine Ecosystems and Fisheries (regional)'


class Water(BaseSector):
    technological_progress = models.TextField(
        null=True, blank=True, default='',
        help_text='Does the model account for GDP changes and technological progress? If so, how are these integrated into the runs?'
    )
    soil_layers = models.TextField(null=True, blank=True, default='',
                                   help_text='How many soil layers are used? Which qualities do they have?')
    water_use = models.TextField(null=True, blank=True, default='', verbose_name='Water-use types',
                                 help_text='Which types of water use are included in the model?')
    water_sectors = models.TextField(
        null=True, blank=True, default='', verbose_name='Water-use sectors',
        help_text='For the global-water-model varsoc and pressoc runs, which water sectors were included? E.g. irrigation, domestic, manufacturing, electricity, livestock.')
    routing = models.TextField(null=True, blank=True, default='', verbose_name='Runoff routing', help_text='How is runoff routed?')
    routing_data = models.TextField(null=True, blank=True, default='', help_text='Which routing data are used?')
    land_use = models.TextField(null=True, blank=True, default='', verbose_name='Land-use change effects',
                                help_text='Which land-use change effects are included?')
    dams_reservoirs = models.TextField(null=True, blank=True, default='', verbose_name='Dam and reservoir implementation',
                                       help_text='Describe how are dams and reservoirs are implemented')

    calibration = models.BooleanField(verbose_name='Was the model calibrated?', default=None, null=True)
    calibration_years = models.TextField(null=True, blank=True, default='', verbose_name='Which years were used for calibration?')
    calibration_dataset = models.TextField(null=True, blank=True, default='', verbose_name='Which dataset was used for calibration?',
                                           help_text='E.g. WFD, GSWP3')
    calibration_catchments = models.TextField(null=True, blank=True, default='',
                                              verbose_name='How many catchments were callibrated?')
    vegetation = models.BooleanField(verbose_name='Is CO2 fertilisation accounted for?', default=None, null=True)
    vegetation_representation = models.TextField(null=True, blank=True, default='', verbose_name='How is vegetation represented?')
    methods_evapotranspiration = models.TextField(null=True, blank=True, default='', verbose_name='Potential evapotranspiration', help_text='Is it implemented? How is it resolved?')
    methods_snowmelt = models.TextField(null=True, blank=True, default='', verbose_name='Snow melt', help_text='Is it implemented? How is it resolved?')

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        generic = super(Water, self).values_to_tuples()
        return [
            ('Technological Progress', [
                (vname('technological_progress'), self.technological_progress),
            ]),
            ('Soil', [
                (vname('soil_layers'), self.soil_layers),
            ]),
            ('Water Use', [
                (vname('water_use'), self.water_use),
                (vname('water_sectors'), self.water_sectors),
            ]),
            ('Routing', [
                (vname('routing'), self.routing),
                (vname('routing_data'), self.routing_data),
            ]),
            ('Land Use', [
                (vname('land_use'), self.land_use),
            ]),
            ('Dams & Reservoirs', [
                (vname('dams_reservoirs'), self.dams_reservoirs),
            ]),
            ('Calibration', [
                (vname('calibration'), self.calibration),
                (vname('calibration_years'), self.calibration_years),
                (vname('calibration_dataset'), self.calibration_dataset),
                (vname('calibration_catchments'), self.calibration_catchments),
            ]),
            ('Vegetation', [
                (vname('vegetation'), self.vegetation),
                (vname('vegetation_representation'), self.vegetation_representation),
            ]),
            ('Methods', [
                (vname('methods_evapotranspiration'), self.methods_evapotranspiration),
                (vname('methods_snowmelt'), self.methods_snowmelt),
            ])
        ] + generic

    class Meta:
        abstract = True


class WaterGlobal(Water):
    class Meta:
        verbose_name = 'Water (global)'
        verbose_name_plural = 'Water (global)'


class WaterRegional(Water):
    VEGETATION_CHOICES = (
        ('prescriped', 'Prescribed'),
        ('simulated', 'Simulated'),
    )
    vegetation_representation = models.CharField(null=True, blank=True, choices=VEGETATION_CHOICES, verbose_name='How is vegetation represented?', max_length=255)
    vegetation_approach_used = models.TextField(null=True, blank=True, default='', verbose_name='Approach used to simulate vegetation dynamics')
    calibration_model_evaluated = models.BooleanField(verbose_name='Was the model validated/evaluated?', default=None, null=True)
    calibration_periods = models.TextField(null=True, blank=True, default='', verbose_name='Calibration and validation periods')
    calibration_methods = models.TextField(null=True, blank=True, default='', verbose_name='Calibration and validation method', help_text='e.g.: Calibration for discharge at the basin outlet, Enhanced calibration for discharge at multiple gauges, etc.')

    class Meta:
        verbose_name = 'Water (regional)'
        verbose_name_plural = 'Water (regional)'

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        generic = super(Water, self).values_to_tuples()
        return [
            ('Methods', [
                (vname('methods_evapotranspiration'), self.methods_evapotranspiration),
                (vname('methods_snowmelt'), self.methods_snowmelt),
            ]),
            ('Vegetation', [
                (vname('vegetation_representation'), self.vegetation_representation),
                (vname('vegetation_approach_used'), self.vegetation_approach_used),
                (vname('vegetation'), self.vegetation),
            ]),
            ('Routing', [
                (vname('routing'), self.routing),
                (vname('routing_data'), self.routing_data),
            ]),
            ('Calibration', [
                (vname('calibration'), self.calibration),
                (vname('calibration_model_evaluated'), self.calibration_model_evaluated),
                (vname('calibration_periods'), self.calibration_periods),
                (vname('calibration_methods'), self.calibration_methods),
            ]),
        ] + generic


class BiodiversityModelOutput(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Biodiversity(BaseSector):
    MODEL_ALGORITHM_CHOICES = (
        ('GAM', 'Generalised Additive Model (GAM)'),
        ('GBM', 'Generalized Boosted Models (GBM)'),
        ('RF', 'Random Forest (RF)'),
        ('MaxEnt', 'Maximum Entropy (MaxEnt)')
    )
    model_algorithm = models.CharField(null=True, blank=True, choices=MODEL_ALGORITHM_CHOICES, verbose_name='Model algorithm', max_length=255)
    explanatory_variables = models.TextField(null=True, blank=True, default='', verbose_name='Explanatory variables')
    RESPONSE_VARIABLE_CHOICES = (
        ('absence/presence of species', 'absence/presence of species'),
        ('species richness of taxon', 'species richness of taxon'),
    )
    response_variable = models.CharField(null=True, blank=True, choices=RESPONSE_VARIABLE_CHOICES, verbose_name='Response variable', max_length=255)
    additional_information_response_variable = models.TextField(null=True, blank=True, default='', verbose_name='Additional information about response variable')
    DISTRIBUTION_RESPONSE_CHOICES = (
        ('Binomial', 'Binomial'),
        ('Bernoulli', 'Bernoulli'),
        ('Poisson', 'Poisson'),
    )
    distribution_response_variable = models.CharField(null=True, blank=True, choices=DISTRIBUTION_RESPONSE_CHOICES, verbose_name='Distribution of response variable', max_length=255)
    parameters = models.TextField(null=True, blank=True, default='', verbose_name='Parameters')
    additional_info_parameters = models.TextField(null=True, blank=True, default='', verbose_name='Additional Information about Parameters')
    SOFTWARE_FUNCTION_CHOICES = (
        ('gam()', 'gam()'),
        ('gbm()', 'gbm()'),
        ('randomForest()', 'randomForest()'),
        ('maxent()', 'maxent()')
    )
    software_function = models.CharField(null=True, blank=True, choices=SOFTWARE_FUNCTION_CHOICES, verbose_name='Software function', max_length=255)
    SOFTWARE_PACKAGE_CHOICES = (
        ('mgcv', 'mgcv'),
        ('gbm', 'gbm'),
        ('dismo', 'dismo'),
        ('randomForest', 'randomForest')
    )
    software_package = models.CharField(null=True, blank=True, choices=SOFTWARE_PACKAGE_CHOICES, verbose_name='Software package', max_length=255)
    software_program = models.TextField(null=True, blank=True, default='', verbose_name='Software program')
    model_output = models.ManyToManyField(BiodiversityModelOutput, blank=True, verbose_name='Model output')
    additional_info_model_output = models.TextField(null=True, blank=True, default='', verbose_name='Additional Information about Model output')

    class Meta:
        verbose_name = 'Biodiversity'
        verbose_name_plural = 'Biodiversity'

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        generic = super(Biodiversity, self).values_to_tuples()
        return [
            ('Model specifications', [
                (vname('model_algorithm'), self.model_algorithm),
                (vname('explanatory_variables'), self.explanatory_variables),
                (vname('response_variable'), self.response_variable),
                (vname('additional_information_response_variable'), self.additional_information_response_variable),
                (vname('distribution_response_variable'), self.distribution_response_variable),
                (vname('parameters'), self.parameters),
                (vname('additional_info_parameters'), self.additional_info_parameters),
                (vname('software_function'), self.software_function),
                (vname('software_package'), self.software_package),
                (vname('software_program'), self.software_program),
                (vname('model_output'), ', '.join([x.name for x in self.model_output.all()])),
                (vname('additional_info_model_output'), self.additional_info_model_output),
            ]),
        ] + generic


class Health(BaseSector):
    pass


class CoastalInfrastructure(BaseSector):
    class Meta:
        verbose_name = 'Coastal Infrastructure'
        verbose_name_plural = 'Coastal Infrastructure'


class Permafrost(BaseSector):
    pass


class ComputableGeneralEquilibriumModelling(BaseSector):
    class Meta:
        verbose_name = verbose_name_plural = 'Computable General Equilibrium Modelling'


class AgroEconomicModelling(BaseSector):
    class Meta:
        verbose_name = verbose_name_plural = 'Agro-Economic Modelling'


class OutputData(models.Model):
    model = models.ForeignKey(ImpactModel, null=True, blank=True, on_delete=models.CASCADE)
    scenarios = models.ManyToManyField(Scenario, blank=True)
    experiments = models.CharField(max_length=1024, null=True, blank=True)
    drivers = models.ManyToManyField(InputData)
    drivers_list = models.CharField(max_length=1024, blank=True, null=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Output data'
        verbose_name = verbose_name_plural = 'Output data'

    def duplicate(self):
        duplicate = OutputData(
            model=self.model,
            experiments=self.experiments,
            date=self.date
        )
        duplicate.save()
        duplicate.scenarios.set(self.scenarios.all())
        duplicate.drivers.set(self.drivers.all())
        return duplicate

    def __str__(self):
        if self.model:
            return "%s : %s" % (self.model.base_model.sector, self.model.base_model.name)
        return "%s" % self.pk


def impact_model_path(instance, filename):
    return 'impact_model_attachments/{0}-{1}'.format(instance.impact_model.id, filename)


class Attachment(models.Model):
    impact_model = models.OneToOneField(ImpactModel, on_delete=models.CASCADE)
    attachment1 = models.FileField(null=True, blank=True, verbose_name="Attachment", upload_to=impact_model_path, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'csv', 'nc'])])
    attachment1_description = models.TextField(null=True, blank=True, verbose_name="Description")
    attachment2 = models.FileField(null=True, blank=True, verbose_name="Attachment", upload_to=impact_model_path, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'csv', 'nc'])])
    attachment2_description = models.TextField(null=True, blank=True, verbose_name="Description")
    attachment3 = models.FileField(null=True, blank=True, verbose_name="Attachment", upload_to=impact_model_path, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'csv', 'nc'])])
    attachment3_description = models.TextField(null=True, blank=True, verbose_name="Description")
    attachment4 = models.FileField(null=True, blank=True, verbose_name="Attachment", upload_to=impact_model_path, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'csv', 'nc'])])
    attachment4_description = models.TextField(null=True, blank=True, verbose_name="Description")
    attachment5 = models.FileField(null=True, blank=True, verbose_name="Attachment", upload_to=impact_model_path, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'csv', 'nc'])])
    attachment5_description = models.TextField(null=True, blank=True, verbose_name="Description")

    def _get_verbose_field_name(self, field):
        fieldmeta = self._meta.get_field(field)
        ret = fieldmeta.verbose_name.title()
        if fieldmeta.help_text:
            ret = generate_helptext(fieldmeta.help_text, ret)
        return ret

    def values_to_tuples(self):
        vname = self._get_verbose_field_name
        tuples = []
        if self.attachment1:
            tuples.append(('', '<a href="%s" target="_blank"><i class="fa fa-download"></i> %s (%s)</a> %s' % (self.attachment1.url, os.path.basename(self.attachment1.name), filesizeformat(self.attachment1.size), self.attachment1_description or '')))
        if self.attachment2:
            tuples.append(('', '<a href="%s" target="_blank"><i class="fa fa-download"></i> %s (%s)</a> %s' % (self.attachment2.url, os.path.basename(self.attachment2.name), filesizeformat(self.attachment2.size), self.attachment2_description or '')))
        if self.attachment3:
            tuples.append(('', '<a href="%s" target="_blank"><i class="fa fa-download"></i> %s (%s)</a> %s' % (self.attachment3.url, os.path.basename(self.attachment3.name), filesizeformat(self.attachment3.size), self.attachment3_description or '')))
        if self.attachment4:
            tuples.append(('', '<a href="%s" target="_blank"><i class="fa fa-download"></i> %s (%s)</a> %s' % (self.attachment4.url, os.path.basename(self.attachment4.name), filesizeformat(self.attachment4.size), self.attachment4_description or '')))
        if self.attachment5:
            tuples.append(('', '<a href="%s" target="_blank"><i class="fa fa-download"></i> %s (%s)</a> %s' % (self.attachment5.url, os.path.basename(self.attachment5.name), filesizeformat(self.attachment5.size), self.attachment5_description or '')))
        return [('Attachments', tuples )]


PUBLICATION_DATE_CHOICES = [
    ('as_soon_as_possible', 'as soon as possible'),
    ('not_before_date', 'not before date'),
    ('one_year_after_dkrz', 'one year after submission to DKRZ at latest'),
    ('notify_isimip', 'the modeling group will notify the ISIMIP data team by email of the end of the emarbo period. (not later than one year after data submission)')
]


class DataPublicationConfirmation(models.Model):
    impact_model = models.OneToOneField(ImpactModel, on_delete=models.PROTECT, related_name='confirmation')
    created = models.DateTimeField(auto_now_add=True)
    email_text = models.TextField(help_text="Please insert information on the experiments that are to be published here (required).")

    is_confirmed = models.BooleanField(default=False)
    confirmed_date = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(User, on_delete=models.CASCADE,  null=True, blank=True)
    confirmed_license = models.CharField(max_length=500, blank=True, null=True)
    confirmed_publication_date = models.CharField(max_length=500, blank=True, null=True, verbose_name="Confirmed publication by", choices=PUBLICATION_DATE_CHOICES)
    confirmed_publication_date_date = models.DateField(blank=True, null=True, verbose_name="Confirmed publication date")

    class Meta:
        verbose_name = "Data publication confirmation"
        verbose_name_plural = "Data publication confirmations"

    @property
    def confirm_url(self):
        from isi_mip.pages.models import ImpactModelsPage
        impage = ImpactModelsPage.objects.get()
        return impage.full_url + impage.reverse_subpage('confirm_data', kwargs={'id': self.impact_model.pk})
