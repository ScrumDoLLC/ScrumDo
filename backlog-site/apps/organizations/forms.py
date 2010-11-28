from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from organizations.models import Organization
from organizations.team_models import Team
from django.forms.extras.widgets import SelectDateWidget

class TeamForm(forms.ModelForm):
  class Meta:
      model = Team
      fields = ('name', 'access_type' )

class OrganizationForm(forms.ModelForm):
  slug = forms.SlugField(max_length=20,
      help_text = _("a short version of the name consisting only of letters, numbers, underscores and hyphens."),
      error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
          
  def clean_slug(self):    
      if Organization.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
        raise forms.ValidationError(_("A Organization already exists with that slug."))        
      return self.cleaned_data["slug"].lower()

  class Meta:
      model = Organization
      fields = ('name', 'slug', 'description' )



class AddUserForm(forms.Form):

  recipient = forms.CharField(label=_(u"User"))

  def __init__(self, *args, **kwargs):
      self.team = kwargs.pop("team")
      super(AddUserForm, self).__init__(*args, **kwargs)

  def clean_recipient(self):
      try:
          user = User.objects.get(username__exact=self.cleaned_data['recipient'])
      except User.DoesNotExist:
          raise forms.ValidationError(_("There is no user with this username."))

      # if ProjectMember.objects.filter(project=self.project, user=user).count() > 0:
      #     raise forms.ValidationError(_("User is already a member of this project."))

      return self.cleaned_data['recipient']

  def save(self, user):
      # new_member = User.objects.get(username__exact=self.cleaned_data['recipient'])
      # project_member = ProjectMember(project=self.project, user=new_member)
      # project_member.save()
      # self.project.members.add(project_member)
      # if notification:
      #     notification.send(self.project.member_users.all(), "projects_new_member", {"new_member": new_member, "project": self.project})
      #     notification.send([new_member], "projects_added_as_member", {"adder": user, "project": self.project})
      # user.message_set.create(message="added %s to project" % new_member)
      pass
