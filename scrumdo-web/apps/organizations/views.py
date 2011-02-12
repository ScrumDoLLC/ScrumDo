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
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings

from organizations.forms import *;

from organizations.models import *;
from organizations.team_models import *;

import organizations.signals as signals

@login_required
def organization(request, organization_slug):
  organization = get_object_or_404(Organization, slug=organization_slug)
  organizations = Organization.getOrganizationsForUser( request.user )

  teams = []
  for team in organization.teams.all():
      teams.append((team, AddUserForm(team=team)))
      
  # this used to live in team_views.py, but since the individual teams pages
  # have been consolodated, this post is now from the organization overview page
  if request.method == "POST":
    action = request.POST.get("action")
    team_id = request.POST.get("team_id")
    team = get_object_or_404(Team, id=team_id)
    if action == "addMember":
      adduser_form = AddUserForm(request.POST, team=team)
      if adduser_form.is_valid():
        adduser_form.save(request.user)
        request.user.message_set.create(message="Member added to team.")               
        adduser_form=AddUserForm(team=team)
    elif action == "addProject":
      project = get_object_or_404( Project, id=request.POST.get("project") )
      team.projects.add(project)
      team.save()
    elif action == "removeProject":
      project = Project.objects.filter(id=request.POST.get("project_id"))[0]
      team.projects.remove(project)
      team.save()
    elif action == "removeUser":
      user = User.objects.filter(id=request.POST.get("user_id"))[0]
      if user == request.user and team.access_type=="admin":
        request.user.message_set.create(message="Can't remove yourself from the team admin group.")               
      else:
        team.members.remove(user);
        team.save()


  return render_to_response("organizations/organization.html", {    
      "organization": organization,
      "organization_teams": teams,
      "organizations": organizations
    }, context_instance=RequestContext(request))


# This is an ajax popup form for editing details of an organization.
@login_required
def organization_edit( request, organization_slug):
  organization = get_object_or_404(Organization, slug=organization_slug)
  if request.method == "POST" and organization.creator == request.user:
    form = UpdateOrganizationForm(request.POST, instance=organization)
    if form.is_valid():
      request.user.message_set.create(message="Organization Updated") 
      form.save()
    else:
      request.user.message_set.create(message="Could not update organization.") 
    
    return HttpResponseRedirect( reverse("organization_detail",kwargs={"organization_slug":organization.slug}))
    
  form = UpdateOrganizationForm(instance=organization)
  organizations = Organization.getOrganizationsForUser( request.user )
  return render_to_response("organizations/organization_form.html", {    
      "organization": organization,
      "organizations": organizations,
      "form":form
    }, context_instance=RequestContext(request))

@login_required
def organization_create(request):
  if request.method == 'POST': # If the form has been submitted...
    form = OrganizationForm( request.POST)
    if form.is_valid(): # All validation rules pass      
      organization = form.save( commit=False )
      organization.creator = request.user
      organization.save()
      
      default_team = Team(organization = organization, name="Owners", access_type="admin")
      default_team.save()
      
      default_team.members.add(request.user)
      default_team.save()
      
      signals.organization_created.send( sender=request, organization=organization )
      
      request.user.message_set.create(message="Organization Created.")               
      return HttpResponseRedirect(reverse("organization_detail",  kwargs={'organization_slug':organization.slug}))
  else:    
    form = OrganizationForm()  
  
  organizations = Organization.getOrganizationsForUser( request.user )
    
  return render_to_response("organizations/create_organization.html", { 
      "organizations": organizations,
      "form": form,
    }, context_instance=RequestContext(request))



@login_required
def team_debug(request):
  read_orgs = Organization.getOrganizationsForUser(request.user)
  admin_orgs = Organization.getAdminOrganizationsForUser(request.user)
  # write_orgs = Organization.getReadWriteOrganizationsForUser(request.user)
  return render_to_response("organizations/team_debug.html", {    
      "read_orgs":read_orgs,
      "admin_orgs":admin_orgs,
    }, context_instance=RequestContext(request))
