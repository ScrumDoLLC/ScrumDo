from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from manager import manager
from projects.access import *


def project_extra_callback(request, extra_slug, project_slug):
  pass


def enable_extra( request, project_slug, extra_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project_slug}))

def disable_extra( request, project_slug, extra_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project_slug}))

def configure_extra( request, project_slug, extra_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project_slug}))

def project_extras(request, project_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  return render_to_response("extras/project_extras.html", {
      "project":project,
      "extras":manager.getExtras()
    }, context_instance=RequestContext(request))

def project_extra_options( request, extra_slug, project_slug):
  pass