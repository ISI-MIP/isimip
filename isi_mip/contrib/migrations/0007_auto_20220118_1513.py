# Generated by Django 3.2.11 on 2022-01-18 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0006_userprofile_show_in_participant_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='orcid_id',
            field=models.CharField(blank=True, help_text='<a href="https://orcid.org/" target="_blank">Open Researcher and Contributor ID</a>, optional.', max_length=500, null=True, verbose_name='ORCID iD'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ror_id',
            field=models.CharField(blank=True, help_text='<a href="https://ror.org/" target="_blank">Research Organization Registry ID</a>, optional, if known', max_length=500, null=True, verbose_name='Institute ROR ID'),
        ),
    ]