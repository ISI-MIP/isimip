from django.forms import ChoiceField, TypedChoiceField
from django.forms.fields import MultipleChoiceField, TypedMultipleChoiceField

from isi_mip.choiceorotherfield.widgets import SelectOrOther


class MyTypedChoiceField(TypedChoiceField):
    widget = SelectOrOther

    def validate(self, value):
        super(ChoiceField, self).validate(value)

        
class MyTypedMultipleChoiceField(TypedMultipleChoiceField):
    widget = SelectOrOther

    def validate(self, value):
        super(MultipleChoiceField, self).validate(value)
