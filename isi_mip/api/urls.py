from django.urls import path

from isi_mip.api.views import impact_model_datacite_api


app_name = 'api'

urlpatterns = [
    path('impactmodels/<int:impactmodel_id>/datacite/', impact_model_datacite_api, name='impact_model_datacite_api'),
]