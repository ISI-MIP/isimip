# Generated by Django 3.2.11 on 2022-02-14 14:12

from django.db import migrations, models
import isi_mip.choiceorotherfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0120_auto_20220131_1127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inputdatainformation',
            name='observed_ocean_climate_data_sets',
        ),
        migrations.RemoveField(
            model_name='inputdatainformation',
            name='simulated_ocean_climate_data_sets',
        ),
        migrations.AddField(
            model_name='marineecosystemsglobal',
            name='observed_ocean_climate_data_sets',
            field=models.ManyToManyField(blank=True, help_text='The observed ocean climate data sets used in this simulation round', related_name='climatemodels_marineecosystemsglobal_observed', to='climatemodels.InputData', verbose_name='Observed ocean climate data sets used'),
        ),
        migrations.AddField(
            model_name='marineecosystemsglobal',
            name='simulated_ocean_climate_data_sets',
            field=models.ManyToManyField(blank=True, help_text='The observed ocean climate data sets used in this simulation round', related_name='climatemodels_marineecosystemsglobal_simulated', to='climatemodels.InputData', verbose_name='Simulated ocean climate data sets used'),
        ),
        migrations.AddField(
            model_name='marineecosystemsregional',
            name='observed_ocean_climate_data_sets',
            field=models.ManyToManyField(blank=True, help_text='The observed ocean climate data sets used in this simulation round', related_name='climatemodels_marineecosystemsregional_observed', to='climatemodels.InputData', verbose_name='Observed ocean climate data sets used'),
        ),
        migrations.AddField(
            model_name='marineecosystemsregional',
            name='simulated_ocean_climate_data_sets',
            field=models.ManyToManyField(blank=True, help_text='The observed ocean climate data sets used in this simulation round', related_name='climatemodels_marineecosystemsregional_simulated', to='climatemodels.InputData', verbose_name='Simulated ocean climate data sets used'),
        ),
        migrations.AlterField(
            model_name='technicalinformation',
            name='spatial_resolution',
            field=isi_mip.choiceorotherfield.models.ChoiceOrOtherField(blank=True, choices=[('0.5’ x 0.5’', '0.5’ x 0.5’'), ('1.5’ x 1.5’', '1.5’ x 1.5’'), ('6.0’ x 6.0’', '6.0’ x 6.0’'), ('0.5°x0.5°', '0.5°x0.5°')], help_text='The spatial resolution at which the ISIMIP simulations were run, if on a regular grid. Data was provided on a 0.5°x0.5° grid', max_length=500, null=True, verbose_name='Spatial Resolution'),
        ),
        migrations.AlterField(
            model_name='technicalinformation',
            name='temporal_resolution_climate',
            field=isi_mip.choiceorotherfield.models.ChoiceOrOtherField(blank=True, choices=[('annual', 'annual'), ('monthly', 'monthly'), ('daily', 'daily'), ('constant', 'constant')], help_text='ISIMIP data was provided in daily time steps', max_length=500, null=True, verbose_name='Temporal resolution of input data: climate variables'),
        ),
    ]