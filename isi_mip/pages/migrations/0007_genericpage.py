# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-25 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import isi_mip.pages.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0028_merge'),
        ('pages', '0006_auto_20160425_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('content', wagtail.core.fields.StreamField((('richtext', wagtail.core.blocks.RichTextBlock()), ('columns_1_to_1', wagtail.core.blocks.StructBlock((('left_column', wagtail.core.blocks.StreamBlock((('rich_text', wagtail.core.blocks.RichTextBlock()), ('link', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock(required=True)), ('picture', wagtail.images.blocks.ImageChooserBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))))), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('faqs', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock()), ('faqs', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('question', wagtail.core.blocks.CharBlock()), ('answer', wagtail.core.blocks.RichTextBlock()))))))))))), ('right_column', wagtail.core.blocks.StreamBlock((('rich_text', wagtail.core.blocks.RichTextBlock()), ('link', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock(required=True)), ('picture', wagtail.images.blocks.ImageChooserBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))))), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('faqs', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock()), ('faqs', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('question', wagtail.core.blocks.CharBlock()), ('answer', wagtail.core.blocks.RichTextBlock()))))))))), form_classname='pull-right'))))), ('columns_1_to_2', wagtail.core.blocks.StructBlock((('left_column', wagtail.core.blocks.StreamBlock((('rich_text', wagtail.core.blocks.RichTextBlock()), ('link', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock(required=True)), ('picture', wagtail.images.blocks.ImageChooserBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))))), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('faqs', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock()), ('faqs', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('question', wagtail.core.blocks.CharBlock()), ('answer', wagtail.core.blocks.RichTextBlock()))))))))))), ('right_column', wagtail.core.blocks.StreamBlock((('rich_text', wagtail.core.blocks.RichTextBlock()), ('link', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock(required=True)), ('picture', wagtail.images.blocks.ImageChooserBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))))), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('faqs', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock()), ('faqs', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('question', wagtail.core.blocks.CharBlock()), ('answer', wagtail.core.blocks.RichTextBlock()))))))))), form_classname='pull-right'))))), ('columns_2_to_1', wagtail.core.blocks.StructBlock((('left_column', wagtail.core.blocks.StreamBlock((('rich_text', wagtail.core.blocks.RichTextBlock()), ('link', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock(required=True)), ('picture', wagtail.images.blocks.ImageChooserBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))))), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('faqs', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock()), ('faqs', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('question', wagtail.core.blocks.CharBlock()), ('answer', wagtail.core.blocks.RichTextBlock()))))))))))), ('right_column', wagtail.core.blocks.StreamBlock((('rich_text', wagtail.core.blocks.RichTextBlock()), ('link', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock(required=True)), ('picture', wagtail.images.blocks.ImageChooserBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))))), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('faqs', wagtail.core.blocks.StructBlock((('title', wagtail.core.blocks.CharBlock()), ('faqs', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock((('question', wagtail.core.blocks.CharBlock()), ('answer', wagtail.core.blocks.RichTextBlock()))))))))), form_classname='pull-right'))))), ('image', isi_mip.pages.blocks.ImageBlock())))),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
