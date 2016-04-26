# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-30 09:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import isi_mip.choiceorotherfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0004_auto_20160322_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimulationRound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpatialAggregation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='impactmodel',
            name='additional_papers',
        ),
        migrations.RemoveField(
            model_name='impactmodel',
            name='natural_vegetation_simulation',
        ),
        migrations.RemoveField(
            model_name='water',
            name='soil',
        ),
        migrations.AddField(
            model_name='impactmodel',
            name='natural_vegetation_dynamics',
            field=models.TextField(blank=True, help_text='Is natural vegetation simulated dynamically? If so, please describe.', null=True),
        ),
        migrations.AddField(
            model_name='impactmodel',
            name='other_references',
            field=models.ManyToManyField(blank=True, null=True, to='climatemodels.ReferencePaper'),
        ),
        migrations.AddField(
            model_name='water',
            name='soil_layers',
            field=models.TextField(blank=True, help_text='How many soil layers are used? Which qualities do they have?', null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='additional_input_data_sets',
            field=models.TextField(blank=True, help_text='List here any data sets used to drive the model that were not provided by ISIMIP', null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='climate_data_sets',
            field=models.ManyToManyField(blank=True, help_text='The climate-input data sets used in this simulation round', to='climatemodels.InputData', verbose_name='Climate data sets used'),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='climate_variables',
            field=models.ManyToManyField(blank=True, help_text='Include variables that were derived from those provided in the ISIMIP input data set', to='climatemodels.ClimateVariable'),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='comments',
            field=models.TextField(blank=True, null=True, verbose_name='Additional comments'),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='exceptions_to_protocol',
            field=models.TextField(blank=True, help_text='Were any settings prescribed by the protocol overruled in order to run the model?', null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='extreme_events',
            field=models.TextField(blank=True, help_text='Which are the key challenges for this model in reproducing impacts of extreme events?', null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='main_reference_paper',
            field=models.ForeignKey(blank=True, help_text='The single paper that should be cited when referring to simulation output from this model', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='main_ref', to='climatemodels.ReferencePaper'),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='management',
            field=models.TextField(blank=True, help_text='Which specific management and autonomous adaptation measures were applied? E.g. varying sowing dates in crop modles, dbh-related harvesting in forest models.', null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='natural_vegetation_cover_dataset',
            field=models.TextField(blank=True, help_text='If natural vegetation cover is prescribed, which dataset is used?', null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='region',
            field=models.ManyToManyField(help_text='For which regions does the model produce results?', to='climatemodels.Region'),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='resolution',
            field=isi_mip.choiceorotherfield.models.ChoiceOrOtherField(blank=True, choices=[('0.5°x0.5°', '0.5°x0.5°')], help_text='The spatial resolution at which the ISIMIP simulations were run, if on a regular grid. Data was provided on a 0.5°x0.5° grid', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='short_description',
            field=models.TextField(blank=True, help_text='This short description should assist other researchers in briefly describing the model in a paper.', null=True, verbose_name='Short model description'),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='socioeconomic_input_variables',
            field=models.ManyToManyField(blank=True, help_text='Include resolution if relevant', to='climatemodels.SocioEconomicInputVariables', verbose_name='Socio-economic input variables'),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='soil_dataset',
            field=models.TextField(blank=True, help_text='HWSD or GSWP3 were provided', null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='spin_up',
            field=models.NullBooleanField(help_text="'No' indicates the simulations were run starting in the first reporting year 1971', verbose_name='Did you spin-up your model?"),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='spin_up_design',
            field=models.TextField(blank=True, help_text='Include the length of the spin up, the CO2 concentration used, and any deviations from the spin-up procedure defined in the protocol.', null=True, verbose_name='Spin-up design'),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='temporal_resolution_climate',
            field=isi_mip.choiceorotherfield.models.ChoiceOrOtherField(blank=True, choices=[('daily', 'daily'), ('monthly', 'monthly'), ('annual', 'annual')], help_text='ISIMIP data was provided in daily time steps', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='temporal_resolution_co2',
            field=isi_mip.choiceorotherfield.models.ChoiceOrOtherField(blank=True, choices=[('annual', 'annual')], help_text='ISIMIP data was provided in annual time steps', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='temporal_resolution_land',
            field=isi_mip.choiceorotherfield.models.ChoiceOrOtherField(blank=True, choices=[('annual', 'annual')], help_text='ISIMIP data was provided in annual time steps', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='impactmodel',
            name='temporal_resolution_soil',
            field=isi_mip.choiceorotherfield.models.ChoiceOrOtherField(blank=True, choices=[('constant', 'constant')], help_text='ISIMIP data was constant in time', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='water',
            name='calibration',
            field=models.NullBooleanField(verbose_name='Was the model calibrated?'),
        ),
        migrations.AlterField(
            model_name='water',
            name='calibration_catchments',
            field=models.TextField(blank=True, null=True, verbose_name='How many catchments were callibrated?'),
        ),
        migrations.AlterField(
            model_name='water',
            name='calibration_dataset',
            field=models.TextField(blank=True, help_text='E.g. WFD, GSWP3', null=True, verbose_name='Which dataset was used for calibration?'),
        ),
        migrations.AlterField(
            model_name='water',
            name='calibration_years',
            field=models.TextField(blank=True, null=True, verbose_name='Which years were used for calibration?'),
        ),
        migrations.AlterField(
            model_name='water',
            name='dams_reservoirs',
            field=models.TextField(blank=True, help_text='Describe how are dams and reservoirs are implemented', null=True, verbose_name='Dams & Reservoirs'),
        ),
        migrations.AlterField(
            model_name='water',
            name='land_use',
            field=models.TextField(blank=True, help_text='Which land-use change effects are included?', null=True, verbose_name='Land-use change effects'),
        ),
        migrations.AlterField(
            model_name='water',
            name='methods_evapotraspiration',
            field=models.TextField(blank=True, null=True, verbose_name='Potential evapotraspiration'),
        ),
        migrations.AlterField(
            model_name='water',
            name='methods_snowmelt',
            field=models.TextField(blank=True, null=True, verbose_name='Snow melt'),
        ),
        migrations.AlterField(
            model_name='water',
            name='routing',
            field=models.TextField(blank=True, help_text='How is runoff routed?', null=True, verbose_name='Runoff routing'),
        ),
        migrations.AlterField(
            model_name='water',
            name='routing_data',
            field=models.TextField(blank=True, help_text='Which routing data are used?', null=True),
        ),
        migrations.AlterField(
            model_name='water',
            name='technological_progress',
            field=models.TextField(blank=True, help_text='Does the model account for GDP changes and technological progress? If so, how are these integrated into the runs?', null=True),
        ),
        migrations.AlterField(
            model_name='water',
            name='vegetation',
            field=models.NullBooleanField(verbose_name='Is CO2 fertilisation accounted for?'),
        ),
        migrations.AlterField(
            model_name='water',
            name='vegetation_presentation',
            field=models.TextField(blank=True, null=True, verbose_name='How is vegetation represented?'),
        ),
        migrations.AlterField(
            model_name='water',
            name='water_sectors',
            field=models.TextField(blank=True, help_text='For the global-water-model varsoc and pressoc runs, which water sectors were included? E.g. irrigation, domestic, manufacturing, electricity, livestock.', null=True, verbose_name='Water-use sectors'),
        ),
        migrations.AlterField(
            model_name='water',
            name='water_use',
            field=models.TextField(blank=True, help_text='Which types of water use are included?', null=True, verbose_name='Water-use types'),
        ),
        migrations.AddField(
            model_name='impactmodel',
            name='simulation_round',
            field=models.ManyToManyField(help_text='For which ISIMIP simulation round are these model details relevant?', to='climatemodels.SimulationRound'),
        ),
        migrations.AddField(
            model_name='impactmodel',
            name='spatial_aggregation',
            field=models.ForeignKey(blank=True, help_text='e.g. regular grid, points, hyrdotopes...', null=True, on_delete=django.db.models.deletion.CASCADE, to='climatemodels.SpatialAggregation'),
        ),
    ]
