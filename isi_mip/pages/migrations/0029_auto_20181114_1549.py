# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-14 14:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import isi_mip.contrib.blocks
import modelcluster.fields
import wagtail.contrib.table_block.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.embeds.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0021_image_file_hash'),
        ('wagtailcore', '0040_page_draft_title'),
        ('pages', '0028_auto_20171207_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaperOverviewPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('content', wagtail.fields.StreamField([('heading', isi_mip.contrib.blocks.HeadingBlock()), ('rich_text', isi_mip.contrib.blocks.RichTextBlock()), ('horizontal_ruler', wagtail.blocks.StreamBlock([])), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('image', isi_mip.contrib.blocks.ImageBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('monospace_text', isi_mip.contrib.blocks.MonospaceTextBlock())], blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='PaperPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('author', models.CharField(max_length=1000)),
                ('journal', models.CharField(max_length=1000)),
                ('link', models.URLField()),
                ('picture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtailimages.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='PaperPageTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='formfield',
            name='field_type',
            field=models.CharField(choices=[('singleline', 'Single line text'), ('multiline', 'Multi-line text'), ('email', 'Email'), ('number', 'Number'), ('url', 'URL'), ('checkbox', 'Checkbox'), ('checkboxes', 'Checkboxes'), ('dropdown', 'Drop down'), ('multiselect', 'Multiple select'), ('radio', 'Radio buttons'), ('date', 'Date'), ('datetime', 'Date/time'), ('hidden', 'Hidden field')], max_length=16, verbose_name='field type'),
        ),
        migrations.AddField(
            model_name='paperpage',
            name='tags',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='pages.PaperPageTag'),
        ),
    ]
