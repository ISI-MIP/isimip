from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.components import Component
from wagtail import hooks

from isi_mip.climatemodels.models import ImpactModel, InputData, OutputData


@hooks.register('insert_editor_css')
def editor_css():
    # Add extra CSS files to the admin like font-awesome
    css_files = [
        'vendor/css/font-awesome.min.css',
        'css/wagtail-font-awesome.css'
    ]

    css_includes = format_html_join(
        '\n',
        '<link rel="stylesheet" href="{0}{1}">',
        ((settings.STATIC_URL, filename) for filename in css_files))

    return css_includes


@hooks.register('insert_editor_js')
def editor_js():
    js_files = [
        'js/hallo-edit-html.js',
    ]
    js_includes = format_html_join(
        '\n', '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files)
    )
    return js_includes + format_html(
        """
        <script>
          registerHalloPlugin('editHtmlButton');
        </script>
        """
    )


class DjangoAdminLinkItem:
    def render(self, request):
        return '<li class="w-userbar__item" role="presentation"><a href="/admin/" target="_parent" role="menuitem" class="action">Django Admin</a></li>'


class LogOutLinkItem:
    def render(self, request):
        return '<li class="w-userbar__item" role="presentation"><a href="/auth/logout/?next=/" target="_parent" role="menuitem" class="action">Logout</a></li>'


@hooks.register('construct_wagtail_userbar')
def add_wagtail_icon_items(request, items):
    items.append(DjangoAdminLinkItem())
    items.append(LogOutLinkItem())


class ImpactModelsPanel(Component):
    order = 50

    def render_html(self, parent_context):
        impactmodels = ImpactModel.objects
        inputdata = InputData.objects
        outputdata = OutputData.objects
        
        output = """<section class="w-summary">
                    <h2 class="visuallyhidden">Impact Model summary</h2>
                    <ul class="w-summary__list">
                    <li>
                        <svg class="icon icon-cogs" aria-hidden="true"><use href="#icon-doc-empty"></use></svg>
                        <a href="/admin/climatemodels/impactmodel/">
                            <span>{}</span> Impact Models
                        </a>
                    </li>
                    <li>
                        <svg class="icon icon-order-down" aria-hidden="true"><use href="#icon-doc-empty"></use></svg>
                        <a href="/admin/climatemodels/inputdata/">
                            <span>{}</span> Input Data sets
                        </a>
                    </li>
                    <li>
                        <svg class="icon icon-order-up" aria-hidden="true"><use href="#icon-doc-empty"></use></svg>
                        <a href="/admin/climatemodels/outputdata/">
                            <span>{}</span> Output Data sets
                        </a>
                    </li>
                    </ul>
                    </section>
                    """.format(impactmodels.count(), inputdata.count(), outputdata.count())

        return mark_safe(output)


@hooks.register('construct_homepage_panels')
def add_impact_models_panel(request, panels):
    return panels.append(ImpactModelsPanel())

@hooks.register('register_admin_menu_item')
def register_frank_menu_item():
  return MenuItem('Django Admin', reverse('admin:index'), icon_name='cogs', order=90000)


@hooks.register('register_admin_menu_item')
def register_questions_menu_item():
  return MenuItem('Model Documentation', '/cms/snippets/climatemodels/impactmodelquestion/' , icon_name='folder-inverse', order=4000)