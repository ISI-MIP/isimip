# Generated by Django 3.2.11 on 2022-01-19 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0043_gettingstartedpage_is_input_data_parent_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gettingstartedpage',
            name='is_input_data_parent_page',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]