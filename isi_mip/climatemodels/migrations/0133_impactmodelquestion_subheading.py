# Generated by Django 3.2.18 on 2023-02-24 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climatemodels', '0132_auto_20230224_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='impactmodelquestion',
            name='subheading',
            field=models.CharField(default='default', max_length=1024),
            preserve_default=False,
        ),
    ]
