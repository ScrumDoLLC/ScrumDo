from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from scrum_log.models import ScrumLog
from django.forms.extras.widgets import SelectDateWidget


class ScrumLogForm(forms.ModelForm):
    def __init__(self,  *args, **kwargs):
        super(ScrumLogForm, self).__init__(*args, **kwargs)
        # self.fields['include_in_velocity'].label = "Include In Velocity Calculations"
    class Meta:
        model = ScrumLog
        fields = ('message', 'message_type', 'flagged' )
