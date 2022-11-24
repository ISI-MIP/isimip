from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe

from isi_mip.climatemodels.models import Sector, BaseImpactModel, ImpactModel


class Role(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)


class Country(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institute = models.CharField(max_length=500, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE,  null=True, blank=True)
    sector = models.ManyToManyField(Sector, blank=True, related_name='user_sectors')
    comment = models.TextField(blank=True, null=True)
    owner = models.ManyToManyField(BaseImpactModel, blank=True, related_name='impact_model_owner', verbose_name='Owner (LEGACY)')
    responsible = models.ManyToManyField(ImpactModel, blank=True, related_name='impact_model_responsible')
    show_in_participant_list = models.BooleanField(default=True)
    orcid_id = models.CharField(max_length=500, null=True, blank=True, verbose_name='ORCID iD', help_text=mark_safe('<a href="https://orcid.org/" target="_blank">Open Researcher and Contributor ID</a>, optional.'))
    ror_id = models.CharField(max_length=500, null=True, blank=True, verbose_name='Institute ROR ID', help_text=mark_safe('<a href="https://ror.org/" target="_blank">Research Organization Registry ID</a>, optional, if known'))

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                p = UserProfile.objects.get(user=self.user)
                self.pk = p.pk
            except UserProfile.DoesNotExist:
                pass

        super(UserProfile, self).save(*args, **kwargs)

    @property
    def name(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return "%s (%s) - %s" % (self.name, self.institute, self.email)

    def pretty(self):
        orcid = ''
        if self.orcid_id:
            orcid = ", <a href='https://orcid.org/{orcid_id}' class='orcid-link' target='_blank'>{orcid_id}</a>".format(orcid_id=self.orcid_id)
        pretty = "<a href='mailto:{0.email}'>{0.email}</a>{2}, {0.institute}{1}".format(self, self.country and " (%s)" % self.country.name or '', orcid)
        return pretty

    class Meta:
        ordering = ('user__last_name',)


def create_profile(sender, instance, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_profile, sender=User)
