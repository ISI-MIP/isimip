from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from isi_mip.climatemodels.models import BaseImpactModel


def impact_model_datacite_api(request, impactmodel_id):
    response = {}
    impact_model = get_object_or_404(BaseImpactModel, pk=impactmodel_id)
    response['titles'] = [
        {
            'title': impact_model.name
        }
    ]
    creators = []
    for creator in impact_model.impact_model_owner.all():
        creator_json = {
            'firstName': creator.user.first_name,
            'givenName': creator.user.last_name,
        }
        affiliation = {}
        if creator.institute:
            affiliation['affiliation'] = creator.institute
        if creator.ror_id:
            affiliation['affiliationIdentifier'] = creator.ror_id
            affiliation['affiliationIdentifierScheme'] = 'ROR'
        creator_json['affiliations'] = (affiliation,)
        if creator.orcid_id:
            creator_json['nameIdentifier'] = creator.orcid_id
            creator_json['nameIdentifierScheme'] = 'ORCID'
        creators.append(creator_json)
    response['creators'] = creators
    related_identifiers = {}
    response['relatedIdentifiers'] = related_identifiers
    return JsonResponse(response, json_dumps_params={'indent': 2})