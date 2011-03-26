# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2011 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from projects.models import Project, ProjectMember, Iteration, Story, Task
from django.forms.extras.widgets import SelectDateWidget

from projects.limits import userIncreasedAlowed


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
        fields = ('velocity_type','point_scale_type', 'use_extra_1', 'use_extra_2', 'use_extra_3', 'use_tasks', 'use_assignee', 'extra_1_label', 'extra_2_label', 'extra_3_label','name', 'description' )

class TaskForm( forms.ModelForm ):
    def __init__(self, project, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        members = project.all_member_choices()
        members.insert(0,("","Nobody"))
        self.fields["assignee"].choices = members
        self.fields["summary"].widget = forms.widgets.TextInput(attrs={'size':'50'})
    class Meta:
        model = Task
        fields = ('complete','summary','assignee')

class AddStoryForm( forms.ModelForm ):
    RANK_CHOICES = (
        ('0', 'Top'),
        ('1', 'Middle'),
        ('2', 'Bottom') )
    project = None
    tags = forms.CharField( required=False )
    general_rank = forms.CharField( required=False, widget=forms.RadioSelect(choices=RANK_CHOICES), initial=2)
    def __init__(self, project, *args, **kwargs):
        super(AddStoryForm, self).__init__(*args, **kwargs)
        self.fields["points"].choices = project.getPointScale()
        self.fields["points"].widget = forms.RadioSelect(choices=project.getPointScale())
        self.fields["summary"].widget = forms.TextInput()
        self.fields["summary"].widget.size = 200
        members = project.all_member_choices()
        members.insert(0,("","---------"))
        self.fields["assignee"].choices = members
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
        return super(AddStoryForm, self).save(**kwargs)
    class Meta:
        model = Story
        fields = ('summary', 'detail', 'tags', 'points' , 'extra_1','extra_2','extra_3','assignee')

class StoryForm( forms.ModelForm ):
    RANK_CHOICES = (
        ('0', 'Top'),
        ('1', 'Middle'),
        ('2', 'Bottom') )
    project = None
    tags = forms.CharField( required=False )
    def __init__(self, project, *args, **kwargs):
        super(StoryForm, self).__init__(*args, **kwargs)
        self.fields["points"].choices = project.getPointScale()
        self.fields["points"].widget = forms.RadioSelect(choices=project.getPointScale())
        self.fields["summary"].widget = forms.TextInput()
        self.fields["summary"].widget.size = 200
        members = project.all_member_choices()
        members.insert(0,("","---------"))
        self.fields["assignee"].choices = members
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

    # def clean_name(self):
    #     if Project.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
    #         raise forms.ValidationError(_("A project already exists with that name."))
    #     return self.cleaned_data["name"]

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

class IterationImportForm(forms.Form):
    import_file  = forms.FileField(required=False)

class IterationImportFormWithUnlock(forms.Form):
    import_file  = forms.FileField(required=False)
    unlock_iteration = forms.BooleanField( required=False, help_text = _("Unlocking the iteration allows users with the appropriate access to edit stories in this iteration.") )

class UnlockForm(forms.Form):
    unlock_iteration = forms.BooleanField( required=False, help_text = _("Unlocking the iteration allows users with the appropriate access to edit stories in this iteration.") )

class ExportForm(forms.Form):
    format = forms.ChoiceField(choices=(("xls","Excel"),("csv","Comma Seperated Value (CSV)"),("xml","XML") ) )
    lock_iteration = forms.BooleanField( required=False, help_text = _("Locking the iteration prevents anyone from editing any stories in it until the iteration is unlocked.") )

class ExportProjectForm(forms.Form):
    format = forms.ChoiceField(initial="sheet", choices=(("sheet","Export each iteration as a seperate sheet."),("combined","Export one combined sheet.") ) , widget=forms.RadioSelect() )



class AddUserForm(forms.Form):

    recipient = forms.CharField(label=_(u"User"))

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        self.user = kwargs.pop("user")
        super(AddUserForm, self).__init__(*args, **kwargs)

    def clean_recipient(self):
        try:
            user = User.objects.get(username__exact=self.cleaned_data['recipient'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("There is no user with this username."))

        if ProjectMember.objects.filter(project=self.project, user=user).count() > 0:
            raise forms.ValidationError(_("User is already a member of this project."))

        if not userIncreasedAlowed(self.project, self.user, user):
            raise forms.ValidationError(_("Upgrade your account to add more users."))

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
