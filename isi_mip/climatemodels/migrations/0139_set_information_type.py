# Generated by Django 3.2.18 on 2023-03-30 09:59

from django.db import migrations


def set_information_type(apps, schema_editor):
    '''
    We can't import the Post model directly as it may be a newer
    version than this migration expects. We use the historical version.
    '''
    ImpactModelQuestion = apps.get_model('climatemodels', 'ImpactModelQuestion')
    ImpactModelQuestion.objects.filter(information_type__isnull=True).update(information_type='sector_specific_information')

class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0138_auto_20230330_1158'),
    ]

    operations = [
        migrations.RunPython(set_information_type),
    ]
