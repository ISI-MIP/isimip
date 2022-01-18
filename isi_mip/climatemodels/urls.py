from django.urls import path, re_path

from isi_mip.climatemodels.views import impact_model_assign, impact_model_assign, crossref_proxy

app_name = 'climatemodels'

urlpatterns = [
    re_path(r'^assign/(?P<username>[^/]*)/$', impact_model_assign, name='assign'),
    path('assign/', impact_model_assign, name='assign'),
    path('crossref/', crossref_proxy, name='crossref'),
]