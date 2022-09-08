import unicodecsv

from django.contrib import admin
from django.contrib import messages
from django.urls import reverse
from django.urls import NoReverseMatch
from django.forms import CheckboxSelectMultiple
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.template import Context, Template
from django.conf import settings

from wagtail.core.models import Site

from isi_mip.sciencepaper.models import Author
from .models import *
from isi_mip.contrib.models import UserProfile
from isi_mip.core.models import DataPublicationRequest
from isi_mip.pages.models import ImpactModelsPage


class HideAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


def get_contact_emails(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contact-persons.csv'
    writer = unicodecsv.writer(response, dialect='excel', delimiter=";", encoding='utf-8')
    writer.writerow(['Simulation Round', 'Impact Model', 'Sector', 'Email', 'Name', 'Institute', 'Country', 'ORCID iD', 'ROR ID'])
    for sr in queryset.all():
        contacts = UserProfile.objects.filter(owner__impact_model__simulation_round=sr).distinct()
        for contact in contacts:
            for model in contact.owner.filter(impact_model__simulation_round=sr):
                writer.writerow([sr.name, model.name, model.sector, contact.email, contact.name, contact.institute, contact.country, contact.orcid_id, contact.ror_id])
    return response
get_contact_emails.short_description = "Get contact persons of selected Simulation Round"


class SimulationRoundAdmin(admin.ModelAdmin):
    model = SimulationRound
    prepopulated_fields = {'slug': ('name',), }
    list_display = ('name', 'order')
    actions = [get_contact_emails]


class HideSectorAdmin(HideAdmin):
    readonly_fields = ('impact_model',)
    exclude = ('data', )


class BaseImpactModelAdmin(admin.ModelAdmin):
    model = BaseImpactModel
    list_display = ('name', 'sector')
    list_filter = ('sector',)
    search_fields = ('name', 'sector__name')


class TechnicalInformationAdmin(admin.StackedInline):
    model = TechnicalInformation


class InputDataInformationAdmin(admin.StackedInline):
    model = InputDataInformation


class OtherInformationAdmin(admin.StackedInline):
    model = OtherInformation


class ImpactModelAdmin(admin.ModelAdmin):
    inlines = [TechnicalInformationAdmin, InputDataInformationAdmin, OtherInformationAdmin]
    model = ImpactModel
    search_fields = ('base_model__name', 'base_model__sector__name', 'simulation_round__name')
    actions = ["duplicate_impact_model"]
    save_on_top = True

    def duplicate_impact_model(self, request, queryset):
        if 'apply' in request.POST:
            impact_model = queryset.first()
            simulation_round_id = request.POST["simulation_round"]
            simulation_round = SimulationRound.objects.get(id=simulation_round_id)
            duplicate = impact_model.duplicate(simulation_round)
            self.message_user(request, "The Impact Model was successfully duplicated")
            return HttpResponseRedirect(reverse("admin:%s_%s_change" % (duplicate._meta.app_label, duplicate._meta.model_name), args=(duplicate.id,)))
        if queryset.count() > 1:
            self.message_user(request, "You can only duplicate one model at a time. Please don't select more then one model.", messages.ERROR)
        elif queryset.count() == 1:
            impact_model = queryset.first()
            simulation_rounds = impact_model.base_model.get_missing_simulation_rounds()
            if not simulation_rounds.exists():
                self.message_user(request, "This Impact Model already exists in every Simulation Round", messages.ERROR)
            else:
                opts = self.model._meta
                app_label = opts.app_label
                context = {
                    "simulation_rounds": simulation_rounds,
                    "impact_model": impact_model,
                    "opts": opts,
                    "app_label": app_label,
                }
                return render(request, 'admin/duplicate_intermediate.html', context=context)
    duplicate_impact_model.short_description = "Duplicate Impact Model"

    def get_name(self, obj):
        return obj.base_model and obj.base_model.name or obj.id
    get_name.admin_order_field = 'base_model__name'
    get_name.short_description = 'Name'

    def get_sector(self, obj):
        return obj.base_model and obj.base_model.sector or None
    get_sector.admin_order_field = 'base_model__sector__name'
    get_sector.short_description = 'Sector'

    def sector_link(self, obj):
        try:
            adminurl = "admin:%s_%s_change" % (obj.fk_sector._meta.app_label, obj.fk_sector._meta.model_name)
            link = reverse(adminurl, args=[obj.fk_sector.id])
            return '<a href="%s">%s</a>' % (link, obj.fk_sector)
        except NoReverseMatch:
            return '<span style="color:#666;">{} has no specific attributes.</span>'.format(obj.fk_sector._meta.verbose_name)
        except KeyError:
            return '<span style="color:#666;">will be shown, once the model is saved.</span>'
    sector_link.allow_tags = True
    sector_link.short_description = 'Sector settings'
    readonly_fields = ('sector_link',)
    list_display = ('get_name', 'simulation_round', 'get_sector', 'public')
    list_filter = ('public', 'base_model__sector',)


class AgricultureAdmin(HideSectorAdmin):
    fieldsets = [
        ('Key input and management', {
            'fields': [
                'crops', 'land_coverage', 'planting_date_decision',
                'planting_density', 'crop_cultivars', 'fertilizer_application',
                'irrigation', 'crop_residue', 'initial_soil_water',
                'initial_soil_nitrate_and_ammonia',
                'initial_soil_C_and_OM', 'initial_crop_residue'
            ]}
         ),
        ('Key model processes', {
            'fields': [
                'lead_area_development', 'light_interception', 'light_utilization', 'yield_formation',
                'crop_phenology', 'root_distribution_over_depth', 'stresses_involved', 'type_of_water_stress',
                'type_of_heat_stress', 'water_dynamics', 'evapo_transpiration', 'soil_CN_modeling',
                'co2_effects',
            ],
        }),
        ('Methods for model calibration and validation', {
            'fields': [
                'parameters_number_and_description', 'calibrated_values', 'output_variable_and_dataset',
                'spatial_scale_of_calibration_validation', 'temporal_scale_of_calibration_validation',
                'criteria_for_evaluation']
        })
    ]


class DataTypeAdmin(admin.ModelAdmin):
    model = DataType
    list_display = ('name', 'is_climate_data_type')
    list_filter = ('is_climate_data_type',)


class SectorAdmin(admin.ModelAdmin):
    model = Sector
    list_display = ('name', 'class_name', 'has_sector_specific_values')
    prepopulated_fields = {'slug': ('name',), }


class SectorInformationFieldAdmin(admin.StackedInline):
    model = SectorInformationField
    prepopulated_fields = {'identifier': ('name',), }


class SectorInformationGroupAdmin(admin.ModelAdmin):
    model = SectorInformationGroup
    inlines = [SectorInformationFieldAdmin]
    prepopulated_fields = {'identifier': ('name',), }

    def get_sector(self, obj):
        return obj.sector.name
    get_sector.admin_order_field = 'sector__name'
    get_sector.short_description = 'Sector'
    list_display = ('get_sector', 'name', 'order')
    list_filter = ('sector__name', )


class InputDataAdmin(admin.ModelAdmin):
    model = InputData
    list_display = ('name', 'protocol_relation', 'data_type', 'get_simulation_round')
    list_filter = ('protocol_relation', 'data_type', 'simulation_round__name')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': ('name', 'protocol_relation', 'data_type', 'variables', 'scenario', 'simulation_round', 'description', 'specification', 'data_source', 'caveats', 'download_instructions', 'data_link', 'doi_link'),
            'description': "The variables are filtered based on the data type. To see variables of a different data type, please change and save data type first."
        }),
    )

    def get_simulation_round(self, obj):
        return ', '.join([sr.name for sr in obj.simulation_round.all()])
    get_simulation_round.admin_order_field = 'simulation_round__name'
    get_simulation_round.short_description = 'Simulation rounds'

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(InputDataAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if request._obj_ and db_field.name == "variables":
            kwargs["queryset"] = ClimateVariable.objects.filter(pk__in=InputData.objects.filter(data_type=request._obj_.data_type).values_list("variables", flat=True))
        return super(InputDataAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class OutputDataAdmin(admin.ModelAdmin):
    model = OutputData
    list_display = ('get_sector', 'get_model', 'get_simulation_round', 'get_drivers', 'experiments')
    list_filter = ('model__base_model__sector__name', 'model__simulation_round__name')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    actions = ["duplicate_output_data"]

    def duplicate_output_data(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, "You can only duplicate one output data set at a time. Please don't select more then one output data.", messages.ERROR)
        elif queryset.count() == 1:
            output_data = queryset.first()
            duplicate = output_data.duplicate()
            self.message_user(request, "The Output Data was successfully duplicated")
            return HttpResponseRedirect(reverse("admin:%s_%s_change" % (duplicate._meta.app_label, duplicate._meta.model_name), args=(duplicate.id,)))
    duplicate_output_data.short_description = "Duplicate Output Data"

    def get_simulation_round(self, obj):
        return obj.model and obj.model.simulation_round or ''
    get_simulation_round.admin_order_field = 'model__simulation_round'
    get_simulation_round.short_description = 'Simulation round'

    def get_sector(self, obj):
        return obj.model and obj.model.base_model.sector.name or ''
    get_sector.admin_order_field = 'model__base_model__sector__name'
    get_sector.short_description = 'Sector'

    def get_model(self, obj):
        return obj.model and obj.model.base_model.name or obj.id
    get_model.admin_order_field = 'model__base_model__name'
    get_model.short_description = 'Impact Model'

    def get_drivers(self, obj):
        return ", ".join([driver.name for driver in obj.drivers.all()])
    get_drivers.admin_order_field = 'drivers__name'
    get_drivers.short_description = 'Input data'


class ClimateVariableAdmin(admin.ModelAdmin):
    model = ClimateVariable

    def get_type(self, obj):
        return ','.join(set(filter(None, [input_data.data_type and input_data.data_type.name for input_data in obj.inputdata_set.all().distinct()])))
    get_type.admin_order_field = 'sector__name'
    get_type.short_description = 'Data type'

    def get_inputdata(self, obj):
        return ','.join(set(filter(None, [input_data.name for input_data in obj.inputdata_set.all().distinct()])))
    get_inputdata.admin_order_field = 'sector__name'
    get_inputdata.short_description = 'Input Data'

    list_display = ('name', 'abbreviation', 'get_type', 'get_inputdata')
    list_filter = ('inputdata__data_type__name',)


class DataPublicationConfirmationModelAdmin(admin.ModelAdmin):
    model = DataPublicationConfirmation
    fields = ('impact_model', 'email_text', 'is_confirmed', 'confirmed_date', 'confirmed_license', 'confirmed_by', 'confirmed_publication_date', 'confirmed_publication_date_date')
    list_display = ('impact_model', 'confirmed_date', 'confirmed_by', 'confirmed_license', 'is_confirmed')
    readonly_fields_edit = ('is_confirmed', 'confirmed_date', 'confirmed_license', 'confirmed_by', 'confirmed_publication_date', 'confirmed_publication_date_date')
    readonly_fields = ('impact_model', 'email_text', 'is_confirmed', 'confirmed_date', 'confirmed_license', 'confirmed_by', 'confirmed_publication_date', 'confirmed_publication_date_date')
    list_filter = ('is_confirmed', 'confirmed_license')
    ordering = ('impact_model',)

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return self.readonly_fields_edit
        else:
            return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "impact_model":
            kwargs["queryset"] = ImpactModel.objects.filter(confirmation__isnull=True)
        return super(DataPublicationConfirmationModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super(DataPublicationConfirmationModelAdmin, self).save_model(request, obj, form, change)
        if not change:
            self.send_request_to_confirm(obj, request)

    def send_request_to_confirm(self, confirmation, request):

        impage = ImpactModelsPage.objects.get()
        for owner in confirmation.impact_model.base_model.impact_model_owner.all():
            link = impage.full_url + impage.reverse_subpage('confirm_data', kwargs={'id': confirmation.impact_model.pk})
            context = {
                'model_contact_person': owner.name,
                'simulation_round': confirmation.impact_model.simulation_round,
                'sector': confirmation.impact_model.base_model.sector,
                'sector_drkz_folder_name': confirmation.impact_model.base_model.sector.drkz_folder_name,
                'impact_model_drkz_folder_name': confirmation.impact_model.base_model.drkz_folder_name,
                'impact_model_name': confirmation.impact_model.base_model.name,
                'data_confirmation_link': link,
                'custom_text': confirmation.email_text,
            }
            site = Site.find_for_request(request)
            confirm_email = DataPublicationRequest.for_site(site)
            confirm_body = Template(confirm_email.body)
            confirm_body = confirm_body.render(Context(context))
            confirm_subject = confirm_email.subject
            owner.user.email_user(confirm_subject, confirm_body, 'ISIMIP Data Confirmation <%s>' % settings.DATA_CONFIRMATION_EMAIL)
        messages.add_message(request, messages.INFO, 'Data confirmation request email have been sent to the owners.')




admin.site.register(BaseImpactModel, BaseImpactModelAdmin)
admin.site.register(ImpactModel, ImpactModelAdmin)
admin.site.register(InputData, InputDataAdmin)
admin.site.register(OutputData, OutputDataAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Agriculture, AgricultureAdmin)
admin.site.register(Energy, HideSectorAdmin)
admin.site.register(WaterGlobal, HideSectorAdmin)
admin.site.register(WaterRegional, HideSectorAdmin)
admin.site.register(Biomes, HideSectorAdmin)
admin.site.register(Forests, HideSectorAdmin)
admin.site.register(MarineEcosystemsGlobal, HideSectorAdmin)
admin.site.register(MarineEcosystemsRegional, HideSectorAdmin)
admin.site.register(Biodiversity, HideSectorAdmin)
admin.site.register(GenericSector, HideSectorAdmin)
admin.site.register(DataPublicationConfirmation, DataPublicationConfirmationModelAdmin)

admin.site.register(SectorInformationGroup, SectorInformationGroupAdmin)

admin.site.register(DataType, DataTypeAdmin)
admin.site.register(ClimateVariable, ClimateVariableAdmin)
admin.site.register(ReferencePaper)
admin.site.register(Author, HideAdmin)
admin.site.register(Region)
admin.site.register(BiodiversityModelOutput)
admin.site.register(Scenario)
admin.site.register(SocioEconomicInputVariables)
admin.site.register(SimulationRound, SimulationRoundAdmin)
admin.site.register(SpatialAggregation)