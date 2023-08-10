# Generated by Django 3.2.18 on 2023-02-23 15:32

from django.db import migrations, models
import django.db.models.deletion
import isi_mip.climatemodels.impact_model_blocks
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0129_outputdata_drivers_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImpactModelInformation',
            fields=[
                ('impact_model', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='climatemodels.impactmodel')),
                ('technical_information', models.JSONField(default=dict)),
                ('input_data_information', models.JSONField(default=dict)),
                ('other_information', models.JSONField(default=dict)),
                ('sector_specific_information', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='ImpactModelQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('information_type', models.CharField(choices=[('technical_information', 'Resolution'), ('input_data_information', 'Input Data'), ('other_information', 'Model Setup')], max_length=255, unique=True)),
                ('questions', wagtail.fields.StreamField([('text', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock(help_text='A unique name identifier for the question', required=True)), ('question', wagtail.blocks.TextBlock(help_text='The question you would like to ask', required=True)), ('required', wagtail.blocks.BooleanBlock(help_text='Is the question you are asking mandatory', required=False))])), ('choice_or_other', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock(help_text='A unique name identifier for the question', required=True)), ('question', wagtail.blocks.TextBlock(help_text='The question you would like to ask', required=True)), ('required', wagtail.blocks.BooleanBlock(help_text='Is the question you are asking mandatory', required=False)), ('choices', wagtail.blocks.ListBlock(isi_mip.climatemodels.impact_model_blocks.ChoiceBlock))])), ('input_data_choice', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock(help_text='A unique name identifier for the question', required=True)), ('question', wagtail.blocks.TextBlock(help_text='The question you would like to ask', required=True)), ('required', wagtail.blocks.BooleanBlock(help_text='Is the question you are asking mandatory', required=False)), ('input_data', wagtail.blocks.MultipleChoiceBlock(choices=isi_mip.climatemodels.impact_model_blocks.get_input_data))]))], blank=True, null=True, use_json_field=None)),
                ('sector', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='climatemodels.sector')),
            ],
        ),
    ]