from django import template
from django.template.loader import render_to_string

from wagtail.core.models import Site

from isi_mip.core.models import FooterLinks

register = template.Library()


@register.simple_tag(takes_context=True)
def footer(context, **kwargs):
    links = []
    if 'request' in context:
        request = context['request']
        site = Site.find_for_request(request)
        if site:
            settings = FooterLinks.for_site(site)

            page = context.get('page')

            for link in settings.footer_links.all():
                name = link.name
                target = link.target.specific
                if page and target == page:
                    active = True
                else:
                    active = False
                if target.url:
                    links.append({'url': target.url + (link.anchor or ''), 'text': name, 'active': active})

    context = {
        'links': links
    }
    template = 'widgets/footer.html'
    return render_to_string(template, context=context)
