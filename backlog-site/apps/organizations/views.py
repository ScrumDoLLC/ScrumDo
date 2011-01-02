# ScrumDo - Agile/Scrum story management web application 
# Copyright (C) 2011 Marc Hughes, Ajay Reddy
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
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
  

@login_required
def organization(request, organization_slug):
  organization = get_object_or_404(Organization, slug=organization_slug)
  
  return render_to_response("organizations/organization.html", {    
      "organization": organization
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
  return render_to_response("organizations/organization_form.html", {    
      "organization": organization,
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
      
      request.user.message_set.create(message="Organization Created.")               
      return HttpResponseRedirect(reverse("organization_detail",  kwargs={'organization_slug':organization.slug}))
  else:
    form = OrganizationForm()  
    
  return render_to_response("organizations/create_organization.html", {    
      "form": form      
    }, context_instance=RequestContext(request))


@login_required
def your_organizations(request):
  organizations = Organization.getOrganizationsForUser( request.user )
#  
  return render_to_response("organizations/organization_list.html", {    
      "organizations": organizations
    }, context_instance=RequestContext(request))



@login_required
def team_debug(request):
  read_orgs = Organization.getOrganizationsForUser(request.user)
  admin_orgs = Organization.getAdminOrganizationsForUser(request.user)
  # write_orgs = Organization.getReadWriteOrganizationsForUser(request.user)
  return render_to_response("organizations/team_debug.html", {    
      "read_orgs":read_orgs,
      "admin_orgs":admin_orgs
    }, context_instance=RequestContext(request))