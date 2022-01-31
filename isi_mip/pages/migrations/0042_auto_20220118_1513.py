# Generated by Django 3.2.11 on 2022-01-18 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0041_auto_20210525_1051'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogindexpage',
            options={'verbose_name': 'Blog index'},
        ),
        migrations.AlterModelOptions(
            name='blogpage',
            options={'verbose_name': 'Blog page', 'verbose_name_plural': 'Blog pages'},
        ),
        migrations.AddField(
            model_name='formfield',
            name='clean_name',
            field=models.CharField(blank=True, default='', help_text='Safe name of the form field, the label converted to ascii_snake_case', max_length=255, verbose_name='name'),
        ),
    ]