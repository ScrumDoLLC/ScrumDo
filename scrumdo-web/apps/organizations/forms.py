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

from organizations.models import Organization, Team
from django.forms.extras.widgets import SelectDateWidget

from projects.limits import org_user_limit

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('name', 'access_type' )


class UpdateOrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = ('name',  'description' )



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
        fields = ('name', 'slug' )



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

        if user in self.team.members.all():
            raise forms.ValidationError(_("User is already a member of this team."))

        if not org_user_limit.increaseAllowed(userToAdd=user, organization=self.team.organization):
            raise forms.ValidationError(_("Upgrade your account to add more users."))

        return self.cleaned_data['recipient']

    def save(self, user):
        new_member = User.objects.get(username__exact=self.cleaned_data['recipient'])
        self.team.members.add( new_member )
        self.team.save()
        user.message_set.create(message="Added %s to team" % new_member)
