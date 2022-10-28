from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.forms import CheckboxSelectMultiple

from isi_mip.climatemodels.models import BaseImpactModel, ImpactModel, SimulationRound
from isi_mip.contrib.models import UserProfile, Role, Country


class RoleAdmin(admin.ModelAdmin):
    model = Role


class CountryAdmin(admin.ModelAdmin):
    model = Country


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user profiles'
    filter_vertical = ('owner', 'responsible')
    filter_horizontal = ('sector', )

    class Media:
        css = {
            'all': ('css/resize-widget.css',),
        }


class SimulationRoundListFilter(admin.SimpleListFilter):

    title = 'Simulation Round'

    parameter_name = 'simulation_round'

    def lookups(self, request, model_admin):
        simulation_rounds = [(sr.id, sr.name) for sr in SimulationRound.objects.all()]
        simulation_rounds.append(('-1', '-'))
        return simulation_rounds

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        elif self.value() == '-1':
            return queryset.filter(userprofile__owner__isnull=True)
        else:
            return queryset.filter()


class UserAdmin(UserAdmin):
    list_display = ('email', 'get_name', 'get_country', 'get_responsible', 'get_sector', 'is_active', 'get_show_in_participant_list')
    # list_filter = ('userprofile__sector', SimulationRoundListFilter)
    list_display_links = ('email', 'get_name')
    list_filter = ()
    search_fields = ('email', 'username', 'first_name', 'last_name', 'userprofile__country__name', 'userprofile__institute', 'userprofile__owner__name', 'userprofile__responsible__base_model__name', 'userprofile__sector__name', 'userprofile__responsible__simulation_round__name')
    inlines = (UserProfileInline, )
    save_on_top = True

    def get_queryset(self, request):
        return super(UserAdmin, self).get_queryset(request).select_related('userprofile').prefetch_related('userprofile__owner', 'userprofile__responsible', 'userprofile__sector', 'userprofile__country')

    def get_responsible(self, obj):
        if obj.userprofile.responsible.exists():
            return ', '.join(['%s(%s)' % (responsible.base_model.name, responsible.simulation_round) for responsible in obj.userprofile.responsible.all()])
        return '-'
    get_responsible.admin_order_field = 'userprofile__responsible__base_model__name'
    get_responsible.short_description = 'Responsible'
    get_responsible.allow_tags = True

    def get_show_in_participant_list(self, obj):
        return obj.userprofile.show_in_participant_list
    get_show_in_participant_list.admin_order_field = 'userprofile__show_in_participant_list'
    get_show_in_participant_list.short_description = 'Show in participant list'
    get_show_in_participant_list.boolean = True

    def get_name(self, obj):
        return '%s %s' % (obj.first_name, obj.last_name)
    get_name.admin_order_field = 'last_name'
    get_name.short_description = 'Name'

    def get_sector(self, obj):
        if obj.userprofile.sector.exists():
            return ', '.join([sector.name for sector in obj.userprofile.sector.all()])
        return '-'
    get_sector.admin_order_field = 'userprofile__sector__name'
    get_sector.short_description = 'Sector'
    get_sector.allow_tags = True

    def get_country(self, obj):
        res = ""
        if obj.userprofile.institute:
            res = obj.userprofile.institute
        if obj.userprofile.country:
            res = res + "(%s)" % obj.userprofile.country.name
        return res
    get_country.admin_order_field = 'userprofile__country__name'
    get_country.short_description = 'Country'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Country, CountryAdmin)
