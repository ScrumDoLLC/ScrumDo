from django import forms
from django.utils.translation import ugettext_lazy as _
  
class GitHubIssuesConfig(forms.Form):
  username = forms.CharField(max_length=100, help_text = _("Your GitHub username."))
  password = forms.CharField(widget=forms.PasswordInput, help_text = _("Your GitHub password.") )
  repository = forms.CharField(help_text = _("Use the user/repository or organization/repository format.  Example: ScrumDo-Dev-Group/ScrumDo"))
  upload = forms.BooleanField(label=_("Upload Stories"),help_text = _("Should ScrumDo stories be created as GitHub issues?"), required=False)
  download = forms.BooleanField(label=_("Download Issues"),help_text = _("Should GitHub issues be created as ScrumDo stories?"), required=False)
  
