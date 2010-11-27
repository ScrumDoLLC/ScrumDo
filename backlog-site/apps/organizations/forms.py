from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from organizations.models import Organization
from django.forms.extras.widgets import SelectDateWidget

class OrganizationForm(forms.ModelForm):
  slug = forms.SlugField(max_length=20,
      help_text = _("a short version of the name consisting only of letters, numbers, underscores and hyphens."),
      error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
          
  def clean_slug(self):
      # if Project.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
      #           raise forms.ValidationError(_("A project already exists with that slug."))
      return self.cleaned_data["slug"].lower()
  

  class Meta:
      model = Organization
      fields = ('name', 'slug', 'description' )
