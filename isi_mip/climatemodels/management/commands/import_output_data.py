import json
import logging
import re
import urllib.request
from datetime import date, datetime

from django.core.management.base import BaseCommand

from isi_mip.climatemodels.models import (ImpactModel, InputData, OutputData,
                                          Sector)
from isi_mip.pages.models import HomePage

logger = logging.getLogger(__name__)



SECTOR_NAME_MAPPING = {
    'LAKES_GLOBAL': 'Lakes (global)',
    'LAKES_LOCAL': 'Lakes (local)',
    'MARINE-FISHERY_GLOBAL': 'Fisheries (global)',
    'MARINE-FISHERY_REGIONAL': 'Fisheries (regional)',
    'WATER_GLOBAL': 'Water (global)',
    'WATER_REGIONAL': 'Water (regional)',
}



class Command(BaseCommand):
    help = 'Imports ISIMIP output data from '


    def update_output_data(self, simulation_round, sector, impact_model, input_data_list, experiment_list, output_data_date, is_public):
        output_data, created = OutputData.objects.get_or_create(model=impact_model)
        experiments = ""
        if not is_public:
            experiments = "(*) "
        experiments += ", ".join(experiment_list)
        output_data.experiments =  experiments
        output_data.drivers_list = ", ".join(input_data_list)
        if not output_data.date:
            output_data.date = output_data_date
        output_data.save()
        print("{}: | {} | {} | {} | {} | {} | {} | {} |".format(created and "CREATE" or "UPDATE", simulation_round, sector, impact_model, input_data_list, experiment_list, output_data_date, is_public))

    def import_output_data(self, simulation_round, url):
        try:
            data = urllib.request.urlopen(url)
            lines = data.read().decode('utf-8').splitlines()
            sector_name = None
            sector_name_not_mapped = None
            last_sector_name_not_mapped = None
            impact_model_name = None
            input_data_name = None
            input_data_list = []
            experiment_list = []
            impact_model = None
            sector = None
            last_sector = None
            output_data_date = None
            output_data = None
            for line in lines:
                # TODO sector is funky, first new model has last sector 
                if line.startswith('* '):
                    sector_name_not_mapped = line.split('* ')[1]
                    if not last_sector_name_not_mapped:
                        last_sector_name_not_mapped = sector_name_not_mapped
                    sector_name = sector_name_not_mapped
                    if sector_name in SECTOR_NAME_MAPPING.keys():
                        sector_name = SECTOR_NAME_MAPPING.get(sector_name)
                    sector = Sector.objects.filter(name__iexact=sector_name).first()
                    if not sector:
                        sector = Sector.objects.filter(drkz_folder_name__iexact=sector_name).first()
                    if not last_sector:
                        last_sector = sector
                    if not sector:
                        print('Sector not found: {}'.format(sector_name))
                    # else:
                        # print(sector)
                if line.startswith(' o '):
                    # new impact model
                    # update data
                    if impact_model:
                        # print('update data: {}'.format(impact_model))
                        api_url = "https://data.isimip.org/api/v1/datasets/?path={}/OutputData/{}/{}".format(simulation_round, last_sector_name_not_mapped.lower(), impact_model_name)
                        is_public = int(json.loads(urllib.request.urlopen(api_url).read().decode('utf-8')).get('count')) > 0
                        self.update_output_data(simulation_round, last_sector, impact_model, input_data_list, experiment_list, output_data_date, is_public)
                        if last_sector_name_not_mapped != sector_name_not_mapped:
                            last_sector = sector
                            last_sector_name_not_mapped = sector_name_not_mapped
                    # reset all variables, new impact model
                    current_date = None
                    output_data_date = None
                    input_data_list = set()
                    experiment_list = set()
                    impact_model_name = line.split(' o ')[1]
                    impact_model = ImpactModel.objects.filter(base_model__sector=sector, base_model__name__iexact=impact_model_name, simulation_round__name__iexact=simulation_round).first()
                    if not impact_model:
                        impact_model = ImpactModel.objects.filter(base_model__sector=sector, base_model__drkz_folder_name__iexact=impact_model_name, simulation_round__name__iexact=simulation_round).first()
                        if not impact_model:
                            print('Impact model not found: {} {} {}'.format(impact_model_name, sector, simulation_round))
                    # else:
                    #     print('found {}'.format(impact_model))
                if line.startswith('  - '):
                    input_data_name = line.split('  - ')[1]
                    input_data_list.add(input_data_name)
                    #     print('InputData found: {}'.format(input_data))
                if line.startswith('     '):
                    result = re.search('(.*) \( (.*) \) \[ (.*) \]', line.strip())
                    experiment = result.group(1)
                    output_data_date_string = result.group(3)
                    current_date = datetime.strptime(output_data_date_string, '%Y-%m-%d').date()
                    if not output_data_date or current_date < output_data_date:
                        output_data_date = current_date
                    # print(experiment, output_data_date)
                    experiment_list.add(experiment)
                    

        except Exception as e:
            print("An error happend while importing from: %s" % url)
            print(e)
            return None

    def handle(self, *args, **options):
        self.import_output_data("ISIMIP3a", "https://www.isimip.org/files/stats/ISIMIP3a/overview_checked.txt")
        self.import_output_data("ISIMIP3b", "https://www.isimip.org/files/stats/ISIMIP3b/overview_checked.txt")
