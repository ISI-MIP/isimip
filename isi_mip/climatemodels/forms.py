from dateutil.parser import parse
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput, inlineformset_factory
from django.utils import text
from django.utils.safestring import mark_safe


from isi_mip.contrib.forms import FieldsetFormMixin
from isi_mip.climatemodels.fields import (MyModelMultipleChoiceField,
                                          MyModelSingleChoiceField)
from isi_mip.climatemodels.models import *
from isi_mip.climatemodels.models import PUBLICATION_DATE_CHOICES
from isi_mip.climatemodels.widgets import (MyBooleanSelect, MyMultiSelect,
                                           MyTextInput, RefPaperWidget)
from isi_mip.contrib.models import Country

ContactPersonFormset = inlineformset_factory(BaseImpactModel, ContactPerson,
                                             extra=1, max_num=2, min_num=1, fields='__all__',
                                             can_delete=False, help_texts='The scientists responsible for performing the simulations for this sector')


class ImpactModelStartForm(forms.ModelForm):
    model = forms.ModelChoiceField(queryset=BaseImpactModel.objects, required=False)
    simulation_round_existing = forms.ModelChoiceField(queryset=SimulationRound.objects, required=False, label='Simulation Round')
    simulation_round_new = forms.ModelChoiceField(queryset=SimulationRound.objects, required=False, label='Simulation Round')
    name = forms.CharField(label='Impact Model Name', required=False)
    sector = forms.ModelChoiceField(queryset=Sector.objects.order_by('name'), required=False)
    send_invitation_email = forms.BooleanField(label='Send the invitation email?', required=False, initial=True)

    class Meta:
        model = ImpactModel
        fields = ('model', 'name', 'sector')


    def clean_name(self):
        name = self.cleaned_data['name']
        if BaseImpactModel.objects.filter(name__iexact=name).exists():
            raise ValidationError("An impact model with this name already exists.")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return name


class BaseImpactModelForm(forms.ModelForm):
    region = MyModelMultipleChoiceField(allowcustom=True, queryset=Region.objects, required=True)

    class Meta:
        model = BaseImpactModel
        exclude = ('owners', 'public', 'sector', 'name', 'drkz_folder_name')
        widgets = {
            'short_description': MyTextInput(textarea=True),
        }


class ImpactModelForm(forms.ModelForm):
    model_output_license = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}), help_text=mark_safe('Please note, if you want to update the model output license please <a href="mailto:info@isimip.org">write to us</a>.'))

    class Meta:
        model = ImpactModel
        fields = ('version', 'model_license', 'model_output_license', 'model_url', 'main_reference_paper', 'other_references', 'additional_persons_involved', 'simulation_round_specific_description')
        # exclude = ('base_model', 'public', 'simulation_round', 'data_download', 'doi')
        widgets = {
            'version': MyTextInput(),
            'main_reference_paper': RefPaperWidget(),
            'other_references': RefPaperWidget(),
            'model_license': MyTextInput(),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'] = {'model_output_license': instance.model_output_license, }
        super().__init__(*args, **kwargs)

    @staticmethod
    def _ref_paper(args):
        if not args['doi'] and not args['title']:
            return None
        if args['doi']:
            try:
                rp = ReferencePaper.objects.get_or_create(doi=args['doi'])[0]
                rp.title = args['title']
            except ReferencePaper.MultipleObjectsReturned:
                rp = ReferencePaper.objects.create(title=args['title'], doi=args['doi'])
        else:
            try:
                rp = ReferencePaper.objects.get_or_create(title=args['title'])[0]
            except ReferencePaper.MultipleObjectsReturned:
                rp = ReferencePaper.objects.create(title=args['title'], doi=args['doi'])
        rp.lead_author = args['lead_author']
        rp.journal_name = args['journal_name']
        rp.journal_volume = args['journal_volume']
        rp.journal_pages = args['journal_pages']
        rp.first_published = args['first_published']
        rp.save()
        return rp

    def clean_main_reference_paper(self):
        try:
            myargs = {
                'lead_author': self.data.getlist('main_reference_paper-author')[0],
                'title': self.data.getlist('main_reference_paper-title')[0],
                'journal_name': self.data.getlist('main_reference_paper-journal')[0],
                'doi': self.data.getlist('main_reference_paper-doi')[0],
                'journal_volume': self.data.getlist('main_reference_paper-volume')[0] or None,
                'journal_pages': self.data.getlist('main_reference_paper-page')[0]
            }
            try:
                myargs['first_published'] = parse(self.data.getlist('main_reference_paper-date')[0])
            except:
                myargs['first_published'] = None
        except:
            raise ValidationError('Problems adding the main reference paper')
        return self._ref_paper(myargs)

    def clean_other_references(self):
        rps = []
        for i in range(len(self.data.getlist('other_references-title')) - 1):
            myargs = {
                'lead_author': self.data.getlist('other_references-author')[i],
                'title': self.data.getlist('other_references-title')[i],
                'journal_name': self.data.getlist('other_references-journal')[i],
                'doi': self.data.getlist('other_references-doi')[i],
                'journal_volume': self.data.getlist('other_references-volume')[i] or None,
                'journal_pages': self.data.getlist('other_references-page')[i]
            }
            try:
                myargs['first_published'] = parse(self.data.getlist('other_references-date')[i])
            except:
                myargs['first_published'] = None

            rp = self._ref_paper(myargs)
            rps += [rp] if rp is not None else []
        return rps


class TechnicalInformationModelForm(forms.ModelForm):
    spatial_aggregation = MyModelSingleChoiceField(allowcustom=True, queryset=SpatialAggregation.objects)

    class Meta:
        model = TechnicalInformation
        exclude = ('impact_model',)
        widgets = {
            'spatial_resolution': MyMultiSelect(allowcustom=True),
            'spatial_resolution_info': MyTextInput(textarea=True),
            'temporal_resolution_climate': MyMultiSelect(allowcustom=True),
            'temporal_resolution_co2': MyMultiSelect(allowcustom=True),
            'temporal_resolution_land': MyMultiSelect(allowcustom=True),
            'temporal_resolution_soil': MyMultiSelect(allowcustom=True),
            'temporal_resolution_info': MyTextInput(textarea=True),
        }


class InputDataInformationModelForm(forms.ModelForm):
    simulated_atmospheric_climate_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
    observed_atmospheric_climate_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
    emissions_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
    socio_economic_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
    land_use_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
    other_human_influences_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
    other_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
    climate_variables = MyModelMultipleChoiceField(allowcustom=False, queryset=ClimateVariable.objects)

    class Meta:
        model = InputDataInformation
        exclude = ('impact_model',)
        widgets = {
            'climate_variables_info': MyTextInput(textarea=True),
            'additional_input_data_sets': MyTextInput(textarea=True),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        simulation_round = instance.impact_model.simulation_round
        super(InputDataInformationModelForm, self).__init__(*args, **kwargs)
        self.fields['climate_variables'].queryset = ClimateVariable.objects.filter(inputdata__data_type__is_climate_data_type=True, inputdata__simulation_round=simulation_round).distinct()
        self.fields['emissions_data_sets'].queryset = InputData.objects.filter(data_type__name='Emissions', simulation_round=simulation_round).distinct()
        self.fields['land_use_data_sets'].queryset = InputData.objects.filter(data_type__name='Land use', simulation_round=simulation_round).distinct()
        self.fields['observed_atmospheric_climate_data_sets'].queryset = InputData.objects.filter(data_type__name='Observed atmospheric climate', simulation_round=simulation_round).distinct()
        self.fields['other_data_sets'].queryset = InputData.objects.filter(data_type__name='Other', simulation_round=simulation_round).distinct()
        self.fields['other_human_influences_data_sets'].queryset = InputData.objects.filter(data_type__name='Other human influences', simulation_round=simulation_round).distinct()
        self.fields['simulated_atmospheric_climate_data_sets'].queryset = InputData.objects.filter(data_type__name='Simulated atmospheric climate', simulation_round=simulation_round).distinct()
        self.fields['socio_economic_data_sets'].queryset = InputData.objects.filter(data_type__name='Socio-economic', simulation_round=simulation_round).distinct()


class OtherInformationModelForm(forms.ModelForm):

    class Meta:
        model = OtherInformation
        exclude = ('impact_model',)
        widgets = {
            'exceptions_to_protocol': MyTextInput(textarea=True),
            'spin_up': MyBooleanSelect(nullable=False),
            'spin_up_design': MyTextInput(textarea=True),
            'natural_vegetation_partition': MyTextInput(textarea=True),
            'natural_vegetation_dynamics': MyTextInput(textarea=True),
            'natural_vegetation_cover_dataset': MyTextInput(),
            'soil_layers': MyTextInput(textarea=True),
            'management': MyTextInput(textarea=True),
            'extreme_events': MyTextInput(textarea=True),
            'anything_else': MyTextInput(textarea=True),
        }


# SEKTOREN ############################################################
class BaseSectorForm(forms.ModelForm):
    generic_fields = []

    class Meta:
        model = GenericSector
        exclude = ('impact_model', 'data')
        abstract = True

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(BaseSectorForm, self).__init__(*args, **kwargs)
        if instance:
            sector = instance.impact_model.base_model.sector
            self.generic_groups = []
            for group in SectorInformationGroup.objects.filter(sector=sector):
                fields = []
                for field in group.fields.all():
                    fields.append(field.unique_identifier)
                    self.generic_fields.append(field.unique_identifier)
                    self.fields[field.unique_identifier] = forms.CharField(widget=MyTextInput(textarea=True), label=field.name, help_text=field.help_text, required=False, initial='')
                    if instance.data and field.unique_identifier in instance.data:
                        field_initial = instance.data[field.unique_identifier]
                        if field_initial:
                            self.fields[field.unique_identifier].initial = field_initial
                self.generic_groups.append({'name': group.name, 'fields': fields, 'description': group.description})

    def clean(self):
        cleaned_data_generic = {}
        cleaned_data = super(BaseSectorForm, self).clean()
        for k in list(cleaned_data.keys()):
            if k in self.generic_fields:
                cleaned_data_generic[k] = cleaned_data[k]
                del cleaned_data[k]
        cleaned_data['data'] = cleaned_data_generic
        return cleaned_data

    def save(self, commit=True):
        instance = super(BaseSectorForm, self).save(commit=False)
        instance.data = self.cleaned_data['data']
        if commit:
            instance.save()
        return instance


class AgricultureForm(BaseSectorForm):
    template = 'edit_agriculture.html'

    class Meta:
        model = Agriculture
        exclude = ('impact_model',)
        widgets = {
            'crops': MyTextInput(textarea=True),
            'land_coverage': MyTextInput(textarea=True),
            'planting_date_decision': MyTextInput(textarea=True),
            'planting_density': MyTextInput(textarea=True),
            'crop_cultivars': MyTextInput(textarea=True),
            'fertilizer_application': MyTextInput(textarea=True),
            'irrigation': MyTextInput(textarea=True),
            'crop_residue': MyTextInput(textarea=True),
            'initial_soil_water': MyTextInput(textarea=True),
            'initial_soil_nitrate_and_ammonia': MyTextInput(textarea=True),
            'initial_soil_C_and_OM': MyTextInput(textarea=True),
            'initial_crop_residue': MyTextInput(textarea=True),
            'lead_area_development': MyTextInput(textarea=True),
            'light_interception': MyTextInput(textarea=True),
            'light_utilization': MyTextInput(textarea=True),
            'yield_formation': MyTextInput(textarea=True),
            'crop_phenology': MyTextInput(textarea=True),
            'root_distribution_over_depth': MyTextInput(textarea=True),
            'stresses_involved': MyTextInput(textarea=True),
            'type_of_water_stress': MyTextInput(textarea=True),
            'type_of_heat_stress': MyTextInput(textarea=True),
            'water_dynamics': MyTextInput(textarea=True),
            'evapo_transpiration': MyTextInput(textarea=True),
            'soil_CN_modeling': MyTextInput(textarea=True),
            'co2_effects': MyTextInput(textarea=True),
            'parameters_number_and_description': MyTextInput(textarea=True),
            'calibrated_values': MyTextInput(textarea=True),
            'output_variable_and_dataset': MyTextInput(textarea=True),
            'spatial_scale_of_calibration_validation': MyTextInput(textarea=True),
            'temporal_scale_of_calibration_validation': MyTextInput(textarea=True),
            'criteria_for_evaluation': MyTextInput(textarea=True),
        }


class ForestsForm(BaseSectorForm):
    template = 'edit_forests.html'
    upload_parameter_list = forms.CharField(widget= MyTextInput(textarea=True), required=False, label=mark_safe('Please upload a list of your parameters as an attachment (Section 7). The list should include species-specific parameters and other parameters not depending on initialization data including the following information: short name, long name, short explanation, unit, value, see here for an example (<a href="http://www.pik-potsdam.de/4c/web_4c/theory/parameter_table_0514.pdf" target="_blank">parameter_table_0514.pdf</a>)'))

    class Meta:
        model = Forests
        exclude = ('impact_model',)
        widgets = {
            # Forest Model Set-up Specifications
            'initialize_model': MyTextInput(textarea=True),
            'data_profound_db': MyTextInput(textarea=True),
            'management_implementation': MyTextInput(textarea=True),
            'harvesting_simulated': MyTextInput(textarea=True),
            'regenerate': MyTextInput(textarea=True),
            'unmanaged_simulations': MyTextInput(textarea=True),
            'noco2_scenario': MyTextInput(textarea=True),
            'leap_years': MyTextInput(textarea=True),
            'simulate_minor_tree': MyTextInput(textarea=True),
            'nitrogen_simulation': MyTextInput(textarea=True),
            'soil_depth': MyTextInput(textarea=True),
            'upload_parameter_list': MyTextInput(textarea=True),
            'minimum_diameter_tree': MyTextInput(textarea=True),
            'model_historically_calibrated': MyTextInput(textarea=True),
            'stochastic_element': MyTextInput(textarea=True),
            # Forest Model Output Specifications
            'initial_state': MyTextInput(textarea=True),
            'total_calculation': MyTextInput(textarea=True),
            'output_dbh_class': MyTextInput(textarea=True),
            'output': MyTextInput(textarea=True),
            'output_per_pft': MyTextInput(),
            'considerations': MyTextInput(textarea=True),
            'dynamic_vegetation': MyTextInput(textarea=True),
            'nitrogen_limitation': MyTextInput(textarea=True),
            'co2_effects': MyTextInput(textarea=True),
            'light_interception': MyTextInput(textarea=True),
            'light_utilization': MyTextInput(textarea=True),
            'phenology': MyTextInput(textarea=True),
            'water_stress': MyTextInput(textarea=True),
            'heat_stress': MyTextInput(textarea=True),
            'evapotranspiration_approach': MyTextInput(textarea=True),
            'rooting_depth_differences': MyTextInput(textarea=True),
            'root_distribution': MyTextInput(textarea=True),
            'permafrost': MyTextInput(textarea=True),
            'closed_energy_balance': MyTextInput(textarea=True),
            'soil_moisture_surface_temperature_coupling': MyTextInput(textarea=True),
            'latent_heat': MyTextInput(textarea=True),
            'sensible_heat': MyTextInput(textarea=True),
            'mortality_age': MyTextInput(textarea=True),
            'mortality_fire': MyTextInput(textarea=True),
            'mortality_drought': MyTextInput(textarea=True),
            'mortality_insects': MyTextInput(textarea=True),
            'mortality_storm': MyTextInput(textarea=True),
            'mortality_stochastic_random_disturbance': MyTextInput(textarea=True),
            'mortality_other': MyTextInput(textarea=True),
            'mortality_remarks': MyTextInput(textarea=True),
            'nbp_fire': MyTextInput(textarea=True),
            'nbp_landuse_change': MyTextInput(textarea=True),
            'nbp_harvest': MyTextInput(textarea=True),
            'nbp_other': MyTextInput(textarea=True),
            'nbp_comments': MyTextInput(textarea=True),
            'list_of_pfts': MyTextInput(textarea=True),
            'pfts_comments': MyTextInput(textarea=True),
            'assimilation': MyTextInput(textarea=True),
            'respiration': MyTextInput(textarea=True),
            'carbon_allocation': MyTextInput(textarea=True),
            'regeneration_planting': MyTextInput(textarea=True),
            'soil_water_balance': MyTextInput(textarea=True),
            'carbon_nitrogen_balance': MyTextInput(textarea=True),
            'feedbacks_considered': MyTextInput(textarea=True),
        }



class BiomesForm(BaseSectorForm):
    template = 'edit_biomes.html'

    class Meta:
        model = Biomes
        exclude = ('impact_model',)
        widgets = {
            'output': MyTextInput(textarea=True),
            'output_per_pft': MyTextInput(),
            'considerations': MyTextInput(textarea=True),
            'dynamic_vegetation': MyTextInput(textarea=True),
            'nitrogen_limitation': MyTextInput(textarea=True),
            'co2_effects': MyTextInput(textarea=True),
            'light_interception': MyTextInput(textarea=True),
            'light_utilization': MyTextInput(textarea=True),
            'phenology': MyTextInput(textarea=True),
            'water_stress': MyTextInput(textarea=True),
            'heat_stress': MyTextInput(textarea=True),
            'evapotranspiration_approach': MyTextInput(textarea=True),
            'rooting_depth_differences': MyTextInput(textarea=True),
            'root_distribution': MyTextInput(textarea=True),
            'permafrost': MyTextInput(textarea=True),
            'closed_energy_balance': MyTextInput(textarea=True),
            'soil_moisture_surface_temperature_coupling': MyTextInput(textarea=True),
            'latent_heat': MyTextInput(textarea=True),
            'sensible_heat': MyTextInput(textarea=True),
            'mortality_age': MyTextInput(textarea=True),
            'mortality_fire': MyTextInput(textarea=True),
            'mortality_drought': MyTextInput(textarea=True),
            'mortality_insects': MyTextInput(textarea=True),
            'mortality_storm': MyTextInput(textarea=True),
            'mortality_stochastic_random_disturbance': MyTextInput(textarea=True),
            'mortality_other': MyTextInput(textarea=True),
            'mortality_remarks': MyTextInput(textarea=True),
            'nbp_fire': MyTextInput(textarea=True),
            'nbp_landuse_change': MyTextInput(textarea=True),
            'nbp_harvest': MyTextInput(textarea=True),
            'nbp_other': MyTextInput(textarea=True),
            'nbp_comments': MyTextInput(textarea=True),
            'list_of_pfts': MyTextInput(textarea=True),
            'pfts_comments': MyTextInput(textarea=True),
            'compute_soil_carbon': MyTextInput(textarea=True),
            'seperate_soil_carbon': MyTextInput(textarea=True),
            'harvest_npp_crops': MyTextInput(textarea=True),
            'treat_biofuel_npp': MyTextInput(textarea=True),
            'npp_litter_output': MyTextInput(textarea=True),
            'simulate_bioenergy': MyTextInput(textarea=True),
            'transition_cropland': MyTextInput(textarea=True),
            'simulate_pasture': MyTextInput(textarea=True),
        }


class FireForm(BaseSectorForm):
    template = 'edit_fire.html'

    class Meta:
        model = Fire
        exclude = ('impact_model',)
        widgets = {
            'output': MyTextInput(textarea=True),
            'output_per_pft': MyTextInput(),
            'considerations': MyTextInput(textarea=True),
            'dynamic_vegetation': MyTextInput(textarea=True),
            'nitrogen_limitation': MyTextInput(textarea=True),
            'co2_effects': MyTextInput(textarea=True),
            'light_interception': MyTextInput(textarea=True),
            'light_utilization': MyTextInput(textarea=True),
            'phenology': MyTextInput(textarea=True),
            'water_stress': MyTextInput(textarea=True),
            'heat_stress': MyTextInput(textarea=True),
            'evapotranspiration_approach': MyTextInput(textarea=True),
            'rooting_depth_differences': MyTextInput(textarea=True),
            'root_distribution': MyTextInput(textarea=True),
            'permafrost': MyTextInput(textarea=True),
            'closed_energy_balance': MyTextInput(textarea=True),
            'soil_moisture_surface_temperature_coupling': MyTextInput(textarea=True),
            'latent_heat': MyTextInput(textarea=True),
            'sensible_heat': MyTextInput(textarea=True),
            'mortality_age': MyTextInput(textarea=True),
            'mortality_fire': MyTextInput(textarea=True),
            'mortality_drought': MyTextInput(textarea=True),
            'mortality_insects': MyTextInput(textarea=True),
            'mortality_storm': MyTextInput(textarea=True),
            'mortality_stochastic_random_disturbance': MyTextInput(textarea=True),
            'mortality_other': MyTextInput(textarea=True),
            'mortality_remarks': MyTextInput(textarea=True),
            'nbp_fire': MyTextInput(textarea=True),
            'nbp_landuse_change': MyTextInput(textarea=True),
            'nbp_harvest': MyTextInput(textarea=True),
            'nbp_other': MyTextInput(textarea=True),
            'nbp_comments': MyTextInput(textarea=True),
            'list_of_pfts': MyTextInput(textarea=True),
            'pfts_comments': MyTextInput(textarea=True),
            'compute_soil_carbon': MyTextInput(textarea=True),
            'seperate_soil_carbon': MyTextInput(textarea=True),
            'harvest_npp_crops': MyTextInput(textarea=True),
            'treat_biofuel_npp': MyTextInput(textarea=True),
            'npp_litter_output': MyTextInput(textarea=True),
            'simulate_bioenergy': MyTextInput(textarea=True),
            'transition_cropland': MyTextInput(textarea=True),
            'simulate_pasture': MyTextInput(textarea=True),
            'main_components_burnt_area': MyTextInput(textarea=True),
            'sources_of_ignition': MyTextInput(textarea=True),
            'fire_ignition_implemented': MyTextInput(textarea=True),
            'natural_ignition_implemented': MyTextInput(textarea=True),
            'human_ignition': MyTextInput(textarea=True),
            'human_ignition_conditions': MyTextInput(textarea=True),
            'how_does_fire_spread': MyTextInput(textarea=True),
            'fire_duration_computed': MyTextInput(textarea=True),
            'model_compute_fuel_load': MyTextInput(textarea=True),
            'list_of_fuel_classes': MyTextInput(textarea=True),
            'fuel_moisture_linked': MyTextInput(textarea=True),
            'carbon_pools_combusted': MyTextInput(textarea=True),
            'combustion_completeness': MyTextInput(textarea=True),
            'min_max_burned_area_grid': MyTextInput(textarea=True),
            'land_cover_classes_allowed': MyTextInput(textarea=True),
            'burned_area_computed_separately': MyTextInput(textarea=True),
            'peatland_fires_included': MyTextInput(textarea=True),
            'deforestation_or_clearing_included': MyTextInput(textarea=True),
            'pastures_represented': MyTextInput(textarea=True),
            'cropland_burn_differ': MyTextInput(textarea=True),
            'pasture_burn_differ': MyTextInput(textarea=True),
            'vegetation_fire_mortality': MyTextInput(textarea=True),
        }


class BiodiversityForm(BaseSectorForm):
    template = 'edit_biodiversity.html'
    model_output = MyModelMultipleChoiceField(allowcustom=True, queryset=BiodiversityModelOutput.objects, required=False)

    class Meta:
        model = Biodiversity
        exclude = ('impact_model',)
        widgets = {
            'model_algorithm': MyMultiSelect(allowcustom=False),
            'explanatory_variables': MyTextInput(textarea=True),
            'response_variable':  MyMultiSelect(allowcustom=False),
            'additional_information_response_variable': MyTextInput(textarea=True),
            'distribution_response_variable':  MyMultiSelect(allowcustom=False),
            'parameters': MyTextInput(textarea=True),
            'additional_info_parameters': MyTextInput(textarea=True),
            'software_function':  MyMultiSelect(allowcustom=False),
            'software_package': MyMultiSelect(allowcustom=False),
            'software_program':  MyTextInput(textarea=True),
            'additional_info_model_output': MyTextInput(textarea=True),
        }


class EnergyForm(BaseSectorForm):
    template = 'edit_energy.html'

    class Meta:
        model = Energy
        exclude = ('impact_model',)
        widgets = {
            'model_type': MyTextInput(textarea=True),
            'temporal_extent': MyTextInput(textarea=True),
            'temporal_resolution': MyTextInput(textarea=True),
            'data_format_for_input': MyTextInput(textarea=True),
            'impact_types_energy_demand': MyTextInput(textarea=True),
            'impact_types_temperature_effects_on_thermal_power': MyTextInput(textarea=True),
            'impact_types_weather_effects_on_renewables': MyTextInput(textarea=True),
            'impact_types_water_scarcity_impacts': MyTextInput(textarea=True),
            'impact_types_other': MyTextInput(textarea=True),
            'output_energy_demand': MyTextInput(textarea=True),
            'output_energy_supply': MyTextInput(textarea=True),
            'output_water_scarcity': MyTextInput(textarea=True),
            'output_economics': MyTextInput(textarea=True),
            'output_other': MyTextInput(textarea=True),
            'variables_not_directly_from_GCMs': MyTextInput(textarea=True),
            'response_function_of_energy_demand_to_HDD_CDD': MyTextInput(textarea=True),
            'factor_definition_and_calculation': MyTextInput(textarea=True),
            'biomass_types': MyTextInput(textarea=True),
            'maximum_potential_assumption': MyTextInput(textarea=True),
            'bioenergy_supply_costs': MyTextInput(textarea=True),
            'socioeconomic_input': MyTextInput(textarea=True),
        }


class MarineEcosystemsForm(BaseSectorForm):
    template = 'edit_marine.html'
    simulated_ocean_climate_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
    observed_ocean_climate_data_sets = MyModelMultipleChoiceField(allowcustom=False, queryset=InputData.objects)
        
    class Meta:
        model = MarineEcosystems
        exclude = ('impact_model',)
        widgets = {
            'defining_features': MyTextInput(textarea=True),
            'spatial_scale': MyTextInput(),
            'spatial_resolution': MyTextInput(),
            'temporal_scale': MyTextInput(),
            'temporal_resolution': MyTextInput(),
            'taxonomic_scope': MyTextInput(),
            'vertical_resolution': MyTextInput(),
            'spatial_dispersal_included': MyTextInput(),
            'fishbase_used_for_mass_length_conversion': MyTextInput(),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        simulation_round = instance.impact_model.simulation_round
        super(MarineEcosystemsForm, self).__init__(*args, **kwargs)
        self.fields['observed_ocean_climate_data_sets'].queryset = InputData.objects.filter(data_type__name='Observed ocean climate', simulation_round=simulation_round).distinct()
        self.fields['simulated_ocean_climate_data_sets'].queryset = InputData.objects.filter(data_type__name='Simulated ocean climate', simulation_round=simulation_round).distinct()



class WaterForm(BaseSectorForm):
    template = 'edit_water.html'

    class Meta:
        model = Water
        exclude = ('impact_model',)
        widgets = {
            'technological_progress': MyTextInput(textarea=True),
            'soil_layers': MyTextInput(textarea=True),
            'water_use': MyTextInput(textarea=True),
            'water_sectors': MyTextInput(textarea=True),
            'routing': MyTextInput(textarea=True),
            'routing_data': MyTextInput(textarea=True),
            'land_use': MyTextInput(textarea=True),
            'dams_reservoirs': MyTextInput(textarea=True),
            'calibration': MyBooleanSelect(nullable=True),
            'calibration_years': MyTextInput(),
            'calibration_dataset': MyTextInput(),
            'calibration_catchments': MyTextInput(),
            'vegetation': MyBooleanSelect(nullable=True),
            'vegetation_representation': MyTextInput(textarea=True),
            "methods_evapotranspiration": MyTextInput(textarea=True),
            'methods_snowmelt': MyTextInput(textarea=True),
        }


class WaterRegionalForm(BaseSectorForm):
    template = 'edit_water_regional.html'

    class Meta:
        model = WaterRegional
        exclude = ('impact_model',)
        widgets = {
            "methods_evapotranspiration": MyTextInput(textarea=True),
            'methods_snowmelt': MyTextInput(textarea=True),
            'vegetation': MyBooleanSelect(nullable=True),
            'vegetation_approach_used': MyTextInput(textarea=True),
            'vegetation_representation': MyMultiSelect(allowcustom=False),
            'routing': MyTextInput(textarea=True),
            'routing_data': MyTextInput(textarea=True),
            'calibration': MyBooleanSelect(nullable=True),
            'calibration_model_evaluated': MyBooleanSelect(nullable=True),
            'calibration_periods': MyTextInput(textarea=True),
            'calibration_methods': MyTextInput(textarea=True),
        }


class GenericSectorForm(BaseSectorForm):
    template = 'edit_generic_sector.html'

    class Meta:
        model = GenericSector
        exclude = ('impact_model', 'data')


def get_sector_form(sector):
    mapping = {
        'agriculture': AgricultureForm,
        'agroeconomicmodelling': GenericSectorForm,
        'biodiversity': BiodiversityForm,
        'biomes': BiomesForm,
        'fire': FireForm,
        'coastalinfrastructure': GenericSectorForm,
        'computablegeneralequilibriummodelling': GenericSectorForm,
        'energy': EnergyForm,
        'forests': ForestsForm,
        'health': GenericSectorForm,
        'marineecosystemsglobal': MarineEcosystemsForm,
        'marineecosystemsregional': MarineEcosystemsForm,
        'permafrost': GenericSectorForm,
        'waterglobal': WaterForm,
        'waterregional': WaterRegionalForm,
        'genericsector': GenericSectorForm,
    }
    return mapping[sector.class_name.lower()]


class ContactInformationForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=60, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}), help_text='If you want to change the contact person or add a new contact person, please contact info@isimip.org.')
    email = forms.EmailField(label='Your email adress', required=True)
    institute = forms.CharField(max_length=500, required=False)
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False, empty_label='-------')
    orcid_id = forms.CharField(max_length=50, required=False, label='ORCID iD', help_text=mark_safe('<a href="https://orcid.org/" target="_blank">Open Researcher and Contributor ID</a>, optional.'))
    ror_id = forms.CharField(max_length=50, required=False, label='Institute ROR ID', help_text=mark_safe('<a href="https://ror.org/" target="_blank">Research Organization Registry ID</a>, optional, if known.'))


class AttachmentModelForm(forms.ModelForm):

    class Meta:
        model = Attachment
        exclude = ('impact_model',)
        widgets = {
            'attachment1': ClearableFileInput,
            'attachment1_description': MyTextInput(),
            'attachment2': ClearableFileInput,
            'attachment2_description': MyTextInput(),
            'attachment3': ClearableFileInput,
            'attachment3_description': MyTextInput(),
            'attachment4': ClearableFileInput,
            'attachment4_description': MyTextInput(),
            'attachment5': ClearableFileInput,
            'attachment5_description': MyTextInput(),
        }


class DataConfirmationForm(forms.Form):
    terms = forms.BooleanField(required=True)
    license = forms.ChoiceField(required=True, choices=(('CC BY 4.0', 'CC BY 4.0'), ('CC0', 'CC0'), ('other', 'other')))
    publication_date = forms.ChoiceField(required=True, choices=PUBLICATION_DATE_CHOICES)
    publication_date_date = forms.DateField(required=False)
    other_license_name = forms.CharField(required=False)
    correct = forms.BooleanField(required=True)


class ImpactModelQuestionForm(FieldsetFormMixin, forms.Form):
    fieldset = []
    def __init__(self, *args, **kwargs):
        impact_model_question = kwargs.pop('impact_model_question')
        simulation_round = kwargs.pop('simulation_round')
        self.fieldset = impact_model_question.fieldset
        super().__init__(*args, **kwargs)
        self.fields = impact_model_question.formfields(simulation_round)