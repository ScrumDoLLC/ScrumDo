from extras.interfaces import ScrumdoProjectExtra
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from django.conf import settings

import forms

import logging

logger = logging.getLogger(__name__)

class GitHubIssuesExtra( ScrumdoProjectExtra ):

  
  
  def __init__(self):
    print "GitHubIssuesExtra created"

  def getName(self):
    return "GitHub Issues"
    
  def getLogo(self):
    return settings.STATIC_URL + "extras/github-logo.png"
    
  # Returns a version of the name consisting of only letters, numbers, or dashes
  def getSlug(self):
    return "github-issues"
      
  # Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user.
  def getDescription(self):
    return "Create ScrumdDo stories for any uncompleted GitHub issue.  Push ScrumDo stories to GitHub issues."
    
  # Should return a django style response that handles any configuration that this extra may need.
  def doProjectConfigration( self, request, project ):
    if request.method == "POST":
      form = forms.GitHubIssuesConfig( request.POST )
      if form.is_valid():
        return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project.slug}))
    else:  
      form = forms.GitHubIssuesConfig()
    return render_to_response("extras/github-issues/configure.html", {
        "project":project,
        "extra":self,
        "form":form
      }, context_instance=RequestContext(request))
    
  # called when an extra is first associated with a project.
  def associate( self, project):
    logger.info("Project associated with GitHubIssuesExtra")

  # called when an extra is removed from a project.
  def unassociate( self, project):
    logger.info("Project unassociated with GitHubIssuesExtra")