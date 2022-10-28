import csv
import time

from django.http import Http404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from isi_mip.contrib.admin import UserAdmin

@login_required
def export_users(request):
    # nasty copy and paste of the admin.py UserAdmin  methods
    def get_res(obj):
        if obj.userprofile.responsible.exists():
            return ', '.join(['%s(%s)' % (responsible.base_model.name, responsible.simulation_round) for responsible in obj.userprofile.responsible.all()])
        return '-'

    def get_show_in_participant_list(obj):
        return obj.userprofile.show_in_participant_list

    def get_name(obj):
        return '%s %s' % (obj.first_name, obj.last_name)

    def get_sector(obj):
        if obj.userprofile.sector.exists():
            return ', '.join([sector.name for sector in obj.userprofile.sector.all()])
        return '-'

    def get_country(obj):
        res = ""
        if obj.userprofile.institute:
            res = obj.userprofile.institute
        if obj.userprofile.country:
            res = res + "(%s)" % obj.userprofile.country.name
        return res
    
    if request.user.is_superuser:
        field_names = ('email', 'get_name', 'get_country', 'get_involved', 'get_sector', 'is_active', 'get_show_in_participant_list')
        queryset = User.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}-{}.csv'.format('users', time.strftime("%Y%m%d-%H%M%S"))
        writer = csv.writer(response)
        # write a header
        writer.writerow(['Email', 'Name', 'Country', 'Responsible', 'Sector', 'Is active?', 'Show in participant list?'])
        for obj in queryset:
            row = []
            for field in field_names:
                if 'get_' in field:
                    row.append(locals()[field](obj))
                else:
                    row.append(getattr(obj, field))
            writer.writerow(row)

        return response
    else:
        raise Http404  
