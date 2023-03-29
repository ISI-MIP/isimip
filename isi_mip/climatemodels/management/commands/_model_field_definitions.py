MODEL_FIELD_DEFINITION = {
    'technical_information': [{
        'heading': 'Technical Information',
        'description': 'This information is specific to each simulation round.',
        'fields': ['spatial_aggregation', 'spatial_resolution', 'spatial_resolution_info', 'temporal_resolution_climate', 'temporal_resolution_co2', 'temporal_resolution_land', 'temporal_resolution_soil', 'temporal_resolution_info'],
    }],
    'input_data_information': [{
        'heading': 'Input data sets used',
        'description': 'Which of these input data sets did you use to drive your model simulations?',
        'fields': ['simulated_atmospheric_climate_data_sets', 'observed_atmospheric_climate_data_sets', 'emissions_data_sets', 'socio_economic_data_sets', 'land_use_data_sets', 'other_human_influences_data_sets', 'other_data_sets', 'additional_input_data_sets', 'climate_variables', 'climate_variables_info'],
    }],
    'other_information': [
        {
            'heading': 'Exceptions to Protocol',
            'description': '',
            'fields': ['exceptions_to_protocol',],
        },
        {
            'heading': 'Spin-up',
            'description': '',
            'fields': ['spin_up', 'spin_up_design'],
        },
        {
            'heading': 'Natural Vegetation',
            'description': '',
            'fields': ['natural_vegetation_partition', 'natural_vegetation_dynamics', 'natural_vegetation_cover_dataset', 'soil_layers'],
        },
        {
            'heading': 'Management & Adaptation Measures',
            'description': '',
            'fields': ['management', ],
        },
        {
            'heading': 'Extreme Events & Disturbances',
            'description': '',
            'fields': ['extreme_events', 'anything_else',],
        },
    ],
    'agriculture': [
        {
            'heading': 'Key input and Management',
            'description': 'Provide a yes/no answer and a short description of how the process is included',
            'fields': ['crops', 'land_coverage', 'planting_date_decision', 'planting_density', 'crop_cultivars', 'fertilizer_application', 'irrigation', 'crop_residue', 'initial_soil_water', 'initial_soil_nitrate_and_ammonia', 'initial_soil_C_and_OM', 'initial_crop_residue', ],
        },
        {
            'heading': 'Key model processes',
            'description': 'Please specify methods for model calibration and validation',
            'fields': ['lead_area_development', 'light_interception', 'light_utilization', 'yield_formation', 'crop_phenology', 'root_distribution_over_depth', 'stresses_involved', 'type_of_water_stress', 'type_of_heat_stress', 'water_dynamics', 'evapo_transpiration', 'soil_CN_modeling', 'co2_effects', ],
        },
        {
            'heading': 'Methods for model calibration and validation',
            'description': 'Please specify methods for model calibration and validation',
            'fields': ['parameters_number_and_description', 'calibrated_values', 'output_variable_and_dataset', 'spatial_scale_of_calibration_validation', 'temporal_scale_of_calibration_validation', 'criteria_for_evaluation', ],
        },
    ],
    'biomes': [
        {
            'heading': 'Model set-up specifications',
            'description': '',
            'fields': ['simulate_bioenergy', 'transition_cropland', 'simulate_pasture'],
        },
        {
            'heading': 'Key model processes',
            'description': 'Please provide yes/no and a short description how the process is included',
            'fields': ['dynamic_vegetation', 'nitrogen_limitation', 'co2_effects', 'light_interception', 'light_utilization', 'phenology', 'water_stress', 'heat_stress', 'evapotranspiration_approach', 'rooting_depth_differences', 'root_distribution', 'closed_energy_balance', 'soil_moisture_surface_temperature_coupling', 'latent_heat', 'sensible_heat', 'compute_soil_carbon', 'seperate_soil_carbon', 'harvest_npp_crops', 'treat_biofuel_npp', 'npp_litter_output', ],
        },
        {
            'heading': 'Causes of mortality in vegetation models',
            'description': 'Describe briefly how the process is described in this model and in which way it is climate dependent.',
            'fields': ['mortality_age', 'mortality_fire', 'mortality_drought', 'mortality_insects', 'mortality_storm', 'mortality_stochastic_random_disturbance', 'mortality_other', 'mortality_remarks', ],
        },
        {
            'heading': 'NBP components',
            'description': 'Indicate whether the model includes the processes, and how the model accounts for the fluxes, i.e. what is the fate of the biomass? E.g. directly to atmsphere or let it go to other pool',
            'fields': ['nbp_fire', 'nbp_landuse_change', 'nbp_harvest', 'nbp_other', 'nbp_comments', ],
        },
        {
            'heading': 'Species / Plant Functional Types (PFTs)',
            'description': '',
            'fields': ['list_of_pfts', 'pfts_comments'],
        },
        {
            'heading': 'Model output specifications',
            'description': '',
            'fields': ['output', 'output_per_pft', 'considerations'],
        },
    ],
    'fire': [
        {
            'heading': 'Fire-specific input data sets',
            'description': '',
            'fields': ['input_datasets_used', 'time_step_fire_model', 'time_step_exchange'],
        },
        {
            'heading': 'Burnt Area',
            'description': '',
            'fields': ['main_components_burnt_area', ],
        },
        {
            'heading': 'Ignition',
            'description': '',
            'fields': ['sources_of_ignition', 'fire_ignition_implemented', 'natural_ignition_implemented', 'human_ignition', 'human_ignition_conditions', ],
        },
        {
            'heading': 'Spread and duration',
            'description': '',
            'fields': ['how_does_fire_spread', 'fire_duration_computed'],
        },
        {
            'heading': 'Fuel load and combustion',
            'description': '',
            'fields': ['model_compute_fuel_load', 'list_of_fuel_classes', 'fuel_moisture_linked', 'carbon_pools_combusted', 'combustion_completeness', ],
        },
        {
            'heading': 'Landcover',
            'description': '',
            'fields': ['min_max_burned_area_grid', 'land_cover_classes_allowed', 'burned_area_computed_separately', 'peatland_fires_included', 'deforestation_or_clearing_included', 'pastures_represented', 'cropland_burn_differ', 'pasture_burn_differ', ],
        },
        {
            'heading': 'Fire mortality',
            'description': '',
            'fields': ['vegetation_fire_mortality', ],
        },
    ],
    'forests': [
        {
            'heading': 'Model set-up specifications',
            'description': '',
            'fields': ['initialize_model', 'data_profound_db', 'management_implementation', 'harvesting_simulated', 'regenerate', 'unmanaged_simulations', 'noco2_scenario', 'leap_years', 'simulate_minor_tree', 'nitrogen_simulation', 'soil_depth', 'stochastic_element', 'minimum_diameter_tree', 'model_historically_calibrated', 'upload_parameter_list', ],
        },
        {
            'heading': 'Key model processes',
            'description': 'Please provide yes/no and a short description how the process is included and it depends on temperature, light, co2, nutrient supply, drought stress and other factors.',
            'fields': [ 'dynamic_vegetation', 'nitrogen_limitation', 'co2_effects', 'light_interception', 'light_utilization', 'phenology', 'water_stress', 'heat_stress', 'evapotranspiration_approach', 'rooting_depth_differences', 'root_distribution', 'closed_energy_balance', 'soil_moisture_surface_temperature_coupling', 'latent_heat', 'sensible_heat', 'assimilation', 'respiration', 'carbon_allocation', 'regeneration_planting', 'soil_water_balance', 'carbon_nitrogen_balance', 'feedbacks_considered',],
        },
        {
            'heading': 'Causes of mortality in vegetation models',
            'description': 'Describe briefly how the process is described in this model and in which way it is climate dependent.',
            'fields': [ 'mortality_age', 'mortality_fire', 'mortality_drought', 'mortality_insects', 'mortality_storm', 'mortality_stochastic_random_disturbance', 'mortality_other', 'mortality_remarks',],
        },
        {
            'heading': 'NBP components',
            'description': 'Indicate whether the model includes the processes, and how the model accounts for the fluxes, i.e. what is the fate of the biomass? E.g. directly to atmsphere or let it go to other pool',
            'fields': ['nbp_fire', 'nbp_landuse_change', 'nbp_harvest', 'nbp_other', 'nbp_comments', ],
        },
        {
            'heading': 'Species / Plant Functional Types (PFTs)',
            'description': '',
            'fields': ['list_of_pfts', 'pfts_comments'],
        },
        {
            'heading': 'Model output specifications',
            'description': '',
            'fields': ['initial_state', 'output', 'output_per_pft', 'total_calculation', 'output_dbh_class', 'considerations',],
        },
    ],
    'energy': [
        {
            'heading': 'Model & Method Characteristics',
            'description': '',
            'fields': ['model_type', 'temporal_extent', 'temporal_resolution', 'data_format_for_input', ],
        },
        {
            'heading': 'Impact Types',
            'description': '',
            'fields': ['impact_types_energy_demand', 'impact_types_temperature_effects_on_thermal_power', 'impact_types_weather_effects_on_renewables', 'impact_types_water_scarcity_impacts', 'impact_types_other', ],
        },
        {
            'heading': 'Output',
            'description': '',
            'fields': ['output_energy_demand', 'output_energy_supply', 'output_water_scarcity', 'output_economics', 'output_other', ],
        },
        {
            'heading': 'Further Information',
            'description': '',
            'fields': ['variables_not_directly_from_GCMs', 'response_function_of_energy_demand_to_HDD_CDD', 'factor_definition_and_calculation', 'biomass_types', 'maximum_potential_assumption', 'bioenergy_supply_costs', 'socioeconomic_input', ],
        },
    ],
    'marine-ecosystems-and-fisheries-global': [
        {
            'heading': '',
            'description': '',
            'fields': ['defining_features', 'spatial_scale', 'spatial_resolution', 'temporal_scale', 'temporal_resolution', 'taxonomic_scope', 'vertical_resolution', 'spatial_dispersal_included', 'fishbase_used_for_mass_length_conversion', 'simulated_ocean_climate_data_sets', 'observed_ocean_climate_data_sets', ],
        },
    ],
    'marine-ecosystems-and-fisheries-regional': [
        {
            'heading': '',
            'description': '',
            'fields': ['defining_features', 'spatial_scale', 'spatial_resolution', 'temporal_scale', 'temporal_resolution', 'taxonomic_scope', 'vertical_resolution', 'spatial_dispersal_included', 'fishbase_used_for_mass_length_conversion', 'simulated_ocean_climate_data_sets', 'observed_ocean_climate_data_sets', ],
        },
    ],
    'lakes-global': [
        {
            'heading': 'Technological Progress',
            'description': '',
            'fields': ['technological_progress', ],
        },
        {
            'heading': 'Soil',
            'description': '',
            'fields': ['soil_layers', ],
        },
        {
            'heading': 'Water Use',
            'description': '',
            'fields': ['water_use', 'water_sectors'],
        },
        {
            'heading': 'Routing',
            'description': '',
            'fields': ['routing', 'routing_data'],
        },
        {
            'heading': 'Land Use',
            'description': '',
            'fields': ['land_use', ],
        },
        {
            'heading': 'Dams & Reservoirs',
            'description': '',
            'fields': ['dams_reservoirs', ],
        },
        {
            'heading': 'Calibration',
            'description': '',
            'fields': [ 'calibration', 'calibration_years', 'calibration_dataset', 'calibration_catchments',],
        },
        {
            'heading': 'Vegetation',
            'description': '',
            'fields': [ 'vegetation', 'vegetation_representation', ],
        },
        {
            'heading': 'Methods',
            'description': '',
            'fields': [ 'methods_evapotranspiration', 'methods_snowmelt',],
        },
    ],
    'lakes-local': [
        {
            'heading': 'Methods',
            'description': '',
            'fields': [ 'methods_evapotranspiration', 'methods_snowmelt',],
        },
        {
            'heading': 'Vegetation',
            'description': '',
            'fields': [ 'vegetation', 'vegetation_representation', ],
        },
        {
            'heading': 'Routing',
            'description': '',
            'fields': ['routing', 'routing_data'],
        },
        {
            'heading': 'Calibration',
            'description': '',
            'fields': [ 'calibration', 'calibration_years', 'calibration_dataset', 'calibration_catchments',],
        },
    ],
    'biodiversity': [
        {
            'heading': 'Model specifications',
            'description': '',
            'fields': ['model_algorithm', 'explanatory_variables', 'response_variable', 'additional_information_response_variable', 'distribution_response_variable', 'parameters', 'additional_info_parameters', 'software_function', 'software_package', 'software_program', 'model_output', 'additional_info_model_output', ],
        },
    ],
    'air-quality': [
    ],
    'coastal-systems': [
    ],
    'permafrost': [
    ],
    'computable-general-equilibrium-modelling': [
    
    ],
    'agro-economic-modelling': [
    ],
}