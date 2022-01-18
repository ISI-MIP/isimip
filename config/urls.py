from __future__ import unicode_literals

from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.contrib.sitemaps.views import sitemap

from isi_mip.climatemodels import urls as climatemodels_urls
from isi_mip.invitation import urls as invitations_urls
from isi_mip.contrib.views import export_users

urlpatterns = [
    path('styleguide/', include("isi_mip.styleguide.urls", namespace="styleguide")),
    re_path(r'^sitemap\.xml$', sitemap),

    path('admin/export/users/', export_users, name='export_users'),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('blog/', include('blog.urls', namespace="blog")),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),


    path('models/', include(climatemodels_urls, namespace='climatemodels')),
    path('accounts/', include(invitations_urls, namespace='accounts')),
    path('api/', include('isi_mip.api.urls', namespace='api')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path('400/', default_views.bad_request, kwargs={'exception': Exception("Bad Request!")}),
        path('403/', default_views.permission_denied, kwargs={'exception': Exception("Permission Denied")}),
        path('404/', default_views.page_not_found, kwargs={'exception': Exception("Page not Found")}),
        path('500/', default_views.server_error),
    ]

urlpatterns += [
    path('', include(wagtail_urls)),
]