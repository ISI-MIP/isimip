from django.urls import path, re_path
from django.urls import reverse
from django.http import HttpResponseRedirect

from isi_mip.invitation.views import InvitationView, RegistrationView


def superuser_required(view):
    def f(request, *args, **kwargs):
        if request.user.is_superuser:
            return view(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('admin:login') + '?next=' + request.META['PATH_INFO'])

    return f

app_name = 'invitation'

urlpatterns = [
    path('invite/', superuser_required(InvitationView.as_view()), name='invite'),
    re_path(r'^register/(?P<pk>\d+)/(?P<token>[0-9a-f]{40})/$', RegistrationView.as_view(), name='register'),
]
