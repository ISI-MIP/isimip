from django.contrib.admin import utils as admin_util
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UsernameField)


class AuthenticationForm(AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': ''}),
        label='Username or email'
    )


class FieldsetBoundField(forms.BoundField):
	"""
	This class extends `django.forms.forms import.BoundField` to also carry information about the fieldset this field is in.
	"""
	
	def __init__(self, form, field, name, fieldset):
		super(FieldsetBoundField, self).__init__(form, field, name)
		self.fieldset = fieldset


class FieldsetFormMixin(object):
	"""
	This mixin class defines methods to use with other form classes to extend them to return `FieldsetBoundField` when accessing
	forms' fields. If such form class has `fieldset` attribute defined it is used to attach fieldset to all fields, which
	are returned as `FieldsetBoundField`.
	
	`fieldset` attribute should have the same structure as that for `django.contrib.admin.ModelAdmin`. The attached fieldset is
	the given fieldset dictionary with `name` set to the name of the fieldset.
	
	It should be listed as the parent class before `django.forms.models.ModelForm` based classes so that methods here take
	precedence.
	"""
	
	def __iter__(self):
		"""
		If `fieldset` attribute is not defined we iterate normally. Otherwise we iterate in the order in which fields
		are defined in `fieldset` attribute. In the later case we return fields as `FieldsetBoundField`.
		"""
		
		if not hasattr(self, 'fieldset'):
			for field in super(FieldsetFormMixin, self).__iter__():
				yield field
		else:
			for field in admin_util.flatten_fieldsets(self.fieldset):
				yield self[field]
	
	def __getitem__(self, name):
		"""
		If `fieldset` attribute is not defined we return the field normally. Otherwise we return the field as `FieldsetBoundField`
		with fieldset attached to it. It the later case the field has to be defined in `fieldset` attribute.
		"""
		
		field = super(FieldsetFormMixin, self).__getitem__(name)
		if not hasattr(self, 'fieldset'):
			return field
		else:
			fieldset = None
			for fname, fset in self.fieldset:
				if name in fset['fields']:
					# We copy dictionary here so that we do not dirty it with later changes
					fieldset = fset.copy()
					fieldset['name'] = fname
					break
			if not fieldset:
				raise KeyError('Key %r not defined in any fieldset in Form' % name)
			return FieldsetBoundField(self, field.field, field.name, fieldset)
