from django.utils import formats
from wagtail.blocks import CharBlock, StructBlock, TextBlock, StreamBlock, PageChooserBlock, \
    URLBlock, DateBlock, ListBlock, BooleanBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock

from isi_mip.contrib.blocks import EmailBlock, IntegerBlock, HeadingBlock, HRBlock, ImageBlock, RichTextBlock, MonospaceTextBlock
from isi_mip.twitter import TwitterTimeline


class RowBlock(StreamBlock):
    class Meta:
        icon = 'horizontalrule'
        template = 'blocks/row_block.html'


BASE_BLOCKS = [
    ('heading', HeadingBlock()),
    ('rich_text', RichTextBlock()),
    ('horizontal_ruler', HRBlock()),
    ('embed', EmbedBlock()),
    ('image', ImageBlock()),
    ('table', TableBlock()),
    ('monospace_text', MonospaceTextBlock())
]


class SmallTeaserBlock(StructBlock):
    title = CharBlock(required=True)
    picture = ImageChooserBlock()
    text = TextBlock(required=True)
    link = PageChooserBlock(required=True)

    class Meta:
        icon = 'fa fa-list-alt'
        template = 'blocks/small_teaser_block.html'

    def get_context(self, value, parent_context=None):
        context = super(SmallTeaserBlock, self).get_context(value, parent_context=parent_context)
        context['title'] = value.get('title')
        image = value.get('picture')
        rendition = image.get_rendition('fill-640x360-c100')
        context['image'] = {'url': rendition.url, 'name': image.title}
        context['href'] = value.get('link').url
        context['description'] = value.get('text')
        context['arrow_right_link'] = True
        return context


class BigTeaserBlock(StructBlock):
    title = CharBlock(required=True)
    subtitle = CharBlock(required=False)
    picture = ImageChooserBlock(required=False)
    full_width_picture = BooleanBlock(required=False, default=False)
    text = RichTextBlock(required=False)
    external_link = URLBlock(required=False, help_text="Will be ignored if an internal link is provided")
    internal_link = PageChooserBlock(required=False, help_text='If set, this has precedence over the external link.')

    from_date = DateBlock(required=False)
    to_date = DateBlock(required=False)

    class Meta:
        icon = 'fa fa-list-alt'
        template = 'blocks/big_teaser_block.html'

    def __init__(self, wideimage=False, local_blocks=None, **kwargs):
        super().__init__(local_blocks=local_blocks, **kwargs)
        self.wideimage = wideimage

    def get_context(self, value, parent_context=None):
        context = super(BigTeaserBlock, self).get_context(value, parent_context=parent_context)
        context['super_title'] = value.get('title')

        image = value.get('picture')
        if image:
            rendition = image.get_rendition('max-800x800')
            context['image'] = {'url': rendition.url, 'name': image.title}
        if value.get('internal_link'):
            context['href'] = value.get('internal_link').url
        else:
            context['href'] = value.get('external_link')
        if context['href']:
            context['text_right_link'] = True
            context['text_right_link_text'] = 'Learn more'

        context.update({
            'title': value.get('subtitle'),
            'description': value.get('text'),
            'divider': value.get('subtitle') and value.get('text'),
            'calendaricon': True,
            'full_width_picture': value.get('full_width_picture'),
        })
        if value.get('from_date') and value.get('to_date'):
            context['date'] = '"{} to {}"'.format(
                formats.date_format(value.get('from_date'), "SHORT_DATE_FORMAT"),
                formats.date_format(value.get('to_date'), "SHORT_DATE_FORMAT")
            )


        context['wideimage'] = self.wideimage
        return context


class _IsiNumberBlock(StructBlock):
    number = CharBlock(required=False, help_text="This number overwrites the imported number (look above) if set.")
    title = CharBlock()
    text = CharBlock()


class IsiNumbersBlock(StructBlock):
    numbers = ListBlock(_IsiNumberBlock())

    class Meta:
        icon = 'form'
        template = 'blocks/isi_numbers_block.html'

    def get_context(self, value, parent_context=None):
        context = super(IsiNumbersBlock, self).get_context(value, parent_context=parent_context)
        page = context['page']
        if page.number1_imported_number and len(context['value']['numbers']) >= 1:
            context['value']['numbers'][0]['number'] = page.number1_imported_number
        if page.number2_imported_number and len(context['value']['numbers']) >= 2:
            context['value']['numbers'][1]['number'] = page.number2_imported_number
        if page.number3_imported_number and len(context['value']['numbers']) >= 3:
            context['value']['numbers'][2]['number'] = page.number3_imported_number
        if page.number4_imported_number and len(context['value']['numbers']) >= 4:
            context['value']['numbers'][3]['number'] = page.number4_imported_number
        
        return context


class TwitterBlock(StructBlock):
    username = CharBlock(required=True)
    count = IntegerBlock(default=20)

    # help_text='You will find username and widget_id @ https://twitter.com/settings/widgets/')
    # widget_id = CharBlock(required=True)
    # tweet_limit = CharBlock(required=True, max_length=2)

    def get_context(self, value, parent_context=None):
        context = super(TwitterBlock, self).get_context(value, parent_context=parent_context)
        twitte = TwitterTimeline(count=(value.get('count')))
        context['timeline'] = twitte.get_timeline(value.get('username'))
        context['username'] = value.get('username') #context['timeline'][0]['screen_name']
        return context

    class Meta:
        icon = 'fa fa-twitter'
        template = 'widgets/twitter.html'


class PaperBlock(StructBlock):
    picture = ImageChooserBlock(required=False)
    author = CharBlock()
    title = CharBlock()
    journal = CharBlock()
    link = URLBlock()

    class Meta:
        icon = 'fa fa-file-text'
        template = 'widgets/page-teaser.html'

    def get_context(self, value, parent_context=None):
        context = super(PaperBlock, self).get_context(value, parent_context=parent_context)
        c_update = {
            'author': value.get('author'),
            'title': value.get('title'),
            'description': value.get('journal'),
            'href': value.get('link'),
            'external_link': True,
            'external_link_text': 'Link',
            'magicgrow': True,
            'border': True,
        }
        context.update(c_update)


        image = value.get('picture')
        if image:
            rendition = image.get_rendition('fill-640x360-c100')
            context['image'] = {'url': rendition.url, 'name': image.title}
        # context['source'] = {'description': 'Link to paper', 'href': value.get('link')}
        return context


class PapersBlock(StructBlock):
    see_all_offset = IntegerBlock(default=8, help_text='Show "See all" after x entries.')
    papers = ListBlock(PaperBlock)

    class Meta:
        icon = 'fa fa-file-text'
        template = 'blocks/outcomes_block.html'


class LinkBlock(StructBlock):
    title = CharBlock(required=True)
    picture = ImageChooserBlock(required=False)
    text = RichTextBlock(required=False)
    link = URLBlock(required=False)
    date = DateBlock(required=False)

    class Meta:
        classname = 'link'
        icon = 'fa fa-external-link'
        template = 'widgets/page-teaser-wide.html'

    def get_context(self, value, parent_context=None):
        context = super(LinkBlock, self).get_context(value, parent_context=parent_context)
        context['arrow_right_link'] = True
        context['title'] = value.get('title')
        context['description'] = value.get('text')
        context['date'] = value.get('date')

        image = value.get('picture')
        if image:
            rendition = image.get_rendition('fill-640x360-c100')
            context['image'] = {'url': rendition.url, 'name': image.title}
        if value.get('link'):
            context['href'] = value.get('link')
        return context


class FAQBlock(StructBlock):
    question = CharBlock()
    answer = RichTextBlock()


class FAQsBlock(StructBlock):
    title = CharBlock()
    faqs = ListBlock(FAQBlock())

    class Meta:
        icon = 'fa fa-medkit'
        template = 'blocks/faq_block.html'

    def get_context(self, value, parent_context=None):
        context = super(FAQsBlock, self).get_context(value, parent_context=parent_context)
        context['titel'] = value.get('title')
        context['list'] = []
        for faq in value.get('faqs'):
            res = {'term': faq.get('question'),
                   'definitions': [{'text': faq.get('answer')}],
                   'opened': False,
                   'notoggle': False
                   }
            context['list'] += [res]
        return context


class ContactBlock(StructBlock):
    name = CharBlock()
    website = URLBlock()
    email = EmailBlock()


class SectorBlock(StructBlock):
    name = CharBlock()
    image = ImageBlock(required=False)
    contacts = ListBlock(ContactBlock)


class ContactsBlock(StructBlock):
    sectors = ListBlock(SectorBlock)

    class Meta:
        icon = 'fa fa-male'
        template = 'blocks/contacts_block.html'

    def get_context(self, value, parent_context=None):
        context = super(ContactsBlock, self).get_context(value, parent_context=parent_context)
        context['sectors'] = []
        for sector in value.get('sectors'):
            sector_dict = {'name': sector.get('name'),
                           'text': ""
                           }
            for contact in sector.get('contacts'):
                n, w, e = contact.get('name'), contact.get('website'), contact.get('email')
                sector_dict['text'] += "<p>{n} <a target='_blank' href='{w}'><i class='fa fa-external-link' aria-hidden='true'></i></a> " \
                                       "<a target='_blank' href='mailto:{e}'><i class='fa fa-envelope' aria-hidden='true'></i></a></p>".format(n=n, w=w, e=e)
            try:
                sector_dict['image'] = {
                    'url': sector.get('image').get_rendition('fill-640x360-c100').url,
                    'name': sector.get('image').title
                }
            except:
                pass

            context['sectors'] += [sector_dict]
        return context


class SupporterBlock(StructBlock):
    name = CharBlock()
    image = ImageBlock(required=False)
    content = RichTextBlock()


class SupportersBlock(StructBlock):
    supporters = ListBlock(SupporterBlock)

    class Meta:
        icon = 'fa fa-male'
        template = 'blocks/supporters_block.html'

    def get_context(self, value, parent_context=None):
        context = super(SupportersBlock, self).get_context(value, parent_context=parent_context)
        context['supporters'] = []
        for supporter in value.get('supporters'):
            supp_dict = {'name': supporter.get('name'),
                         'text': supporter.get('content')
                         }
            # for contact in supporter.get('contacts'):
            #     n, w, e = contact.get('name'), contact.get('website'), contact.get('email')
            #     supp_dict['text'] += "<p>{n} <a target='_blank' href='{w}'><i class='fa fa-external-link' aria-hidden='true'></i></a> " \
            #                            "<a target='_blank' href='mailto:{e}'><i class='fa fa-envelope' aria-hidden='true'></i></a></p>".format(n=n, w=w, e=e)
            try:
                supp_dict['image'] = {
                    'url': supporter.get('image').get_rendition('fill-500x500-c100').url,
                    'name': supporter.get('image').title
                }
            except:
                pass

            context['supporters'] += [supp_dict]
        return context


class PDFBlock(StructBlock):
    file = DocumentChooserBlock()
    description = CharBlock()

    def get_context(self, value, parent_context=None):
        context = super(PDFBlock, self).get_context(value, parent_context=parent_context)
        context['button'] = {
            'text': 'Download',
            'href': value.get('file').url
        }
        context['description'] = value.get('description')
        context['fontawesome'] = 'file-pdf-o'
        return context

    class Meta:
        icon = 'fa fa-file-pdf-o'
        template = 'widgets/download-link.html'


# def render_basic(self, value):
#         ret = super().render_basic(value)
#         if ret:
#             ret = 'PDF' + ret
#         return ret


class ProtocolBlock(StructBlock):
    complete_pdf = DocumentChooserBlock(label='Complete PDF')
    pdfs = ListBlock(PDFBlock(), label='Chapter PDFs')
    image = ImageBlock()
    version = CharBlock()

    class Meta:
        icon = 'fa fa-newspaper-o'
        template = 'blocks/protocol_block.html'

    def get_context(self, value, parent_context=None):
        context = super(ProtocolBlock, self).get_context(value, parent_context=parent_context)
        context['links'] = []
        for pdf in value.get('pdfs'):
            context['links'] += [{
                'fontawesome': 'file-pdf-o',
                'href': pdf.get('file').url,
                'text': pdf.get('description')
            }]
        try:
            rendition = value.get('image').get_rendition('max-500x500')
            context['image'] = {'url': rendition.url, 'name': value.get('image').title}
        except:
            pass
        return context


_COLUMNS_BLOCKS = BASE_BLOCKS + [
    ('small_teaser', SmallTeaserBlock()),
    ('big_teaser', BigTeaserBlock()),
    ('isinumbers', IsiNumbersBlock()),
    ('link', LinkBlock()),
    ('faqs', FAQsBlock()),
    ('pdf', PDFBlock()),
]


class ColumnsBlock(StructBlock):
    left_column = StreamBlock(_COLUMNS_BLOCKS)
    right_column = StreamBlock(_COLUMNS_BLOCKS)  # , form_classname='pull-right')

    def get_context(self, value, parent_context=None):
        context = super(ColumnsBlock, self).get_context(value, parent_context=parent_context)
        context['left_column'] = value.get('left_column')
        context['right_column'] = value.get('right_column')
        return context

    class Meta:
        icon = 'fa fa-columns'
        label = 'Columns 1-1'
        template = None


class Columns1To1Block(ColumnsBlock):
    class Meta:
        label = 'Columns 1:1'
        template = 'widgets/columns-1-1.html'


class Columns1To2Block(ColumnsBlock):
    class Meta:
        label = 'Columns 1:2'
        template = 'widgets/columns-1-2.html'


class Columns2To1Block(ColumnsBlock):
    class Meta:
        label = 'Columns 2:1'
        template = 'widgets/columns-2-1.html'


class Columns1To1To1Block(ColumnsBlock):
    center_column = StreamBlock(_COLUMNS_BLOCKS)

    class Meta:
        label = 'Columns 1:1:1'
        template = 'widgets/columns-1-1-1.html'

    def get_context(self, value):
        context = super().get_context(value)
        context['center_column'] = value.get('center_column')
        return context


class Columns1To1To1To1Block(StructBlock):
    first_column = StreamBlock(_COLUMNS_BLOCKS)
    second_column = StreamBlock(_COLUMNS_BLOCKS)
    third_column = StreamBlock(_COLUMNS_BLOCKS)
    fourth_column = StreamBlock(_COLUMNS_BLOCKS)

    class Meta:
        icon = 'fa fa-columns'
        label = 'Columns 1:1:1:1'
        template = 'widgets/columns-1-1-1-1.html'

    def get_context(self, value, parent_context=None):
        context = super(Columns1To1To1To1Block, self).get_context(value, parent_context=parent_context)
        context['first_column'] = value.get('first_column')
        context['second_column'] = value.get('second_column')
        context['third_column'] = value.get('third_column')
        context['fourth_column'] = value.get('fourth_column')
        return context


COLUMNS_BLOCKS = [
    ('columns_1_to_1', Columns1To1Block()),
    ('columns_1_to_2', Columns1To2Block()),
    ('columns_2_to_1', Columns2To1Block()),
    ('columns_1_to_1_to_1', Columns1To1To1Block()),
    ('columns_1_to_1_to_1_to_1', Columns1To1To1To1Block()),

]
