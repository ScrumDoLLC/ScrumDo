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

