from django import forms
from api.models import DeveloperApiKey

class DeveloperApiKeyForm(forms.ModelForm):
    class Meta:
        model = DeveloperApiKey
        fields = ('application_name',)
