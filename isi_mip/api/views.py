from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from isi_mip.climatemodels.models import BaseImpactModel


def impact_model_datacite_api(request, impactmodel_id):
    response = {}
    base_impact_model = get_object_or_404(BaseImpactModel, pk=impactmodel_id)
    # response['titles'] = [
    titles = [{
        'title': base_impact_model.name
    }]
    creators = []
    for creator in base_impact_model.impact_model_owner.all():
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
    for impact_model in base_impact_model.impact_model.all():
        related_identifiers = []
        if impact_model.model_url:
            related_identifiers.append({
                "title": "Model Homepage {}".format(impact_model.base_model.name),
                "relationType": "IsDocumentedBy",
                "relatedIdentifier": impact_model.model_url,
                "relatedIdentifierType": "URL"
            })
        if impact_model.main_reference_paper:
            related_identifiers.append({
                "title": impact_model.main_reference_paper.entry(),
                "relationType": "IsDocumentedBy",
                "relatedIdentifier": impact_model.main_reference_paper.doi,
                "relatedIdentifierType": "DOI"
            })
        for paper in impact_model.other_references.all():
            related_identifiers.append({
                "title": paper.entry(),
                "relationType": "Cites",
                "relatedIdentifier": paper.doi,
                "relatedIdentifierType": "DOI"
            })

        response[impact_model.simulation_round.name] = {
            "titles": titles,
            "version": impact_model.version,
            "creators": creators,
            "related_identifiers": related_identifiers,
        }
    return JsonResponse(response, json_dumps_params={'indent': 2})