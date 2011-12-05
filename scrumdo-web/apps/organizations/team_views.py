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

from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.forms.fields import email_re
import random
import string

from projects.models import Project
from organizations.forms import *
from organizations.models import *
from pinax.core.utils import get_send_mail
from pinax.core.utils import get_send_mail
send_mail = get_send_mail()



def _isAdmin( user, organization ):
    return Organization.objects.filter( teams__members = user , teams__access_type="admin", teams__organization=organization).count() > 0

@login_required
def team_add_project(request, organization_slug, team_id ):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied() # Shenanigans
    project_id = request.POST.get("project")
    project = get_object_or_404(Project, id=project_id)    
    if project.organization != organization:
        raise PermissionDenied() # Shenanigans
    team.projects.add(project)
    return team_detail(request, organization_slug, team_id)
    
    
@login_required
def team_invite_accept(request, key):
    invite = get_object_or_404(TeamInvite, key=key)
    team = invite.team
    team.members.add( request.user )
    invite.delete()
    return HttpResponseRedirect(reverse("organization_detail", kwargs={"organization_slug":team.organization.slug} ))
    
@login_required
def team_invite(request, organization_slug, team_id ):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied() # Shenanigans!
    userinput = request.POST.get("invitee")
    
    users = User.objects.filter(username__iexact=userinput)
    if len(users) == 0:
        users = User.objects.filter(email__iexact=userinput)
    
    if len(users) > 0:        
        new_member = users[0]
        team.members.add( new_member )
        team.save()
        return team_detail(request, organization_slug, team_id)
    
    if email_re.match( userinput ):
        key = ''.join(random.choice(string.letters + string.digits) for i in xrange(8))
        invite = TeamInvite(email_address=userinput, team=team, key=key)
        invite.save()
        
        subject = _("Invtation to ScrumDo team")
        message = render_to_string("organizations/team_invite_email.txt", {
            "invite": invite,
            "inviter": request.user
        })

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [userinput])
        
    return team_detail(request, organization_slug, team_id)
        


@login_required
def team_remove_project(request, organization_slug, team_id, project_id):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied() # Shenanigans!
    project = Project.objects.get(id=project_id) 
    team.projects.remove(project)
    return HttpResponse("OK")

@login_required    
def team_remove_member(request, organization_slug, team_id, member_id):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied() # Shenanigans!
    
    user = User.objects.filter(id=member_id)[0]
    if user == request.user and team.access_type=="staff":
        return HttpResponse("Can't remove yourself from the staff group.")
    else:
        team.members.remove(user);
        team.save()
    return HttpResponse("OK")
    
@login_required   
def team_summary(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    organizations = Organization.getOrganizationsForUser( request.user )
    if organization.hasStaffAccess(request.user):
        teams = organization.teams.all().order_by("name")
    else:
        teams = organization.teams.filter(members=request.user).order_by("name")

    return render_to_response("organizations/organization_teams.html", {
        "organization": organization,
        "organizations": organizations,
        "teams": teams
      }, context_instance=RequestContext(request))

@login_required   
def team_detail(request, organization_slug, team_id):
    organization = get_object_or_404(Organization, slug=organization_slug)    
    team = get_object_or_404(Team, id=team_id)
    
    if not (organization.hasStaffAccess( request.user ) or team.hasMember(request.user) ):
        raise PermissionDenied()
    

    if team.organization != organization:
        raise PermissionDenied() # Shenanigans!
        
    organizations = Organization.getOrganizationsForUser( request.user )
    
    return render_to_response("organizations/organization_team.html", {
        "team": team,
        "organization": organization,
        "organizations": organizations,
      }, context_instance=RequestContext(request))

@login_required   
def team_delete(request, organization_slug, team_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    team = get_object_or_404(Team, id=team_id)
    if team.organization != organization:
        raise PermissionDenied()
    team.delete()
    return HttpResponse("Deleted")

@login_required   
def team_create(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if request.method == 'POST': # If the form has been submitted...
        form = TeamForm( request.POST)
        if form.is_valid(): # All validation rules pass
            team = form.save( commit=False )
            team.organization = organization
            team.save()

            request.user.message_set.create(message="Team Created.")
            return HttpResponseRedirect(reverse("team_summary",  kwargs={'organization_slug':organization.slug}))
    else:
        form = TeamForm()

    organizations = Organization.getOrganizationsForUser( request.user )

    return render_to_response("organizations/create_team.html", {
        "form": form,
        "organization": organization,
        "organizations": organizations,
      }, context_instance=RequestContext(request))
