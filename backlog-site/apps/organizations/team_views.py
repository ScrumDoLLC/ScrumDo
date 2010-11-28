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

from organizations.forms import *
from organizations.models import *
from organizations.team_models import *

from organizations.forms import AddUserForm

def team(request, organization_slug, team_id):
  organization  = get_object_or_404(Organization, slug=organization_slug)
  team = get_object_or_404(Team, id=team_id)
  adduser_form=AddUserForm(team=team)
  return render_to_response("organizations/team.html", {    
      "organization": organization,
      "team": team,
      "adduser_form":adduser_form
    }, context_instance=RequestContext(request))
  
def team_create(request, organization_slug):
  organization = get_object_or_404(Organization, slug=organization_slug)
  
  if request.method == 'POST': # If the form has been submitted...
    form = TeamForm( request.POST)
    if form.is_valid(): # All validation rules pass      
      team = form.save( commit=False )
      team.organization = organization
      team.save()

      request.user.message_set.create(message="Team Created.")               
      return HttpResponseRedirect(reverse("organization_detail",  kwargs={'organization_slug':organization.slug}))
  else:
    form = TeamForm()
  


  return render_to_response("organizations/create_team.html", {    
      "form": form
    }, context_instance=RequestContext(request))