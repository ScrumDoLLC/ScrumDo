from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from projects.models import Project, ProjectMember, Iteration, Story
from django.forms.extras.widgets import SelectDateWidget




if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

# @@@ we should have auto slugs, even if suggested and overrideable

class IterationForm(forms.ModelForm):
  def __init__(self,  *args, **kwargs):
    super(IterationForm, self).__init__(*args, **kwargs)
    
    self.fields['include_in_velocity'].label = "Include In Velocity Calculations"
    # self.fields['end_date'].widget = SelectDateWidget()
    
  class Meta:
      model = Iteration
      fields = ('name', 'detail', 'start_date', 'end_date', 'include_in_velocity')



class ProjectOptionsForm(forms.ModelForm):
  class Meta:
      model = Project
      fields = ('use_extra_1', 'use_extra_2', 'use_extra_3', 'use_acceptance', 'use_assignee', 'extra_1_label', 'extra_2_label', 'extra_3_label','name', 'description' )


class StoryForm( forms.ModelForm ):
  RANK_CHOICES = (
      ('0', 'Top'), 
      ('1', 'Middle'),
      ('2', 'Bottom') )
  project = None      
  tags = forms.CharField( required=False )
  general_rank = forms.CharField( required=False, widget=forms.RadioSelect(choices=RANK_CHOICES), initial=2)
  
  def __init__(self, project, *args, **kwargs):    
    super(StoryForm, self).__init__(*args, **kwargs)      
    self.fields["points"].choices = self.instance.POINT_CHOICES    
    self.fields["points"].widget = forms.RadioSelect(choices=self.instance.POINT_CHOICES)
    self.fields["summary"].widget = forms.TextInput()
    self.fields["summary"].widget.size = 200
    self.fields["assignee"].queryset = project.member_queryset().order_by("username")    
    self.fields["extra_1"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50}) 
    self.fields["extra_2"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50}) 
    self.fields["extra_3"].widget = forms.widgets.Textarea(attrs={'rows':3, 'cols':50})         
    self.fields["assignee"].required = False
    self.fields["extra_1"].required = False
    self.fields["extra_2"].required = False
    self.fields["extra_3"].required = False
    self.fields["tags"].initial = self.instance.tags

  
  def save(self,  **kwargs):
    self.instance.tags = self.cleaned_data["tags"]
    return super(StoryForm, self).save(**kwargs)
  
  class Meta:
      model = Story
      fields = ('summary', 'detail', 'tags', 'points' , 'extra_1','extra_2','extra_3','assignee')


class ProjectForm(forms.ModelForm):
    
    slug = forms.SlugField(max_length=20,
        help_text = _("a short version of the name consisting only of letters, numbers, underscores and hyphens."),
        error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
    
    def clean_slug(self):
        if Project.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
            raise forms.ValidationError(_("A project already exists with that slug."))
        return self.cleaned_data["slug"].lower()
    
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ('name', 'slug', 'description')


# @@@ is this the right approach, to have two forms where creation and update fields differ?

class ProjectUpdateForm(forms.ModelForm):
    
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            if self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ('name', 'description')

class ImportForm(forms.Form):
  file  = forms.FileField()
  
class AddUserForm(forms.Form):
    
    recipient = forms.CharField(label=_(u"User"))
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super(AddUserForm, self).__init__(*args, **kwargs)
    
    def clean_recipient(self):
        try:
            user = User.objects.get(username__exact=self.cleaned_data['recipient'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("There is no user with this username."))
        
        if ProjectMember.objects.filter(project=self.project, user=user).count() > 0:
            raise forms.ValidationError(_("User is already a member of this project."))
        
        return self.cleaned_data['recipient']
    
    def save(self, user):
        new_member = User.objects.get(username__exact=self.cleaned_data['recipient'])
        project_member = ProjectMember(project=self.project, user=new_member)
        project_member.save()
        self.project.members.add(project_member)
        if notification:
            notification.send(self.project.member_users.all(), "projects_new_member", {"new_member": new_member, "project": self.project})
            notification.send([new_member], "projects_added_as_member", {"adder": user, "project": self.project})
        user.message_set.create(message="added %s to project" % new_member)
