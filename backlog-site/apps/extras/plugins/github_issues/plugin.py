from extras.interfaces import ScrumdoProjectExtra
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.conf import settings

import forms
import logging



from extras.plugins.github_issues.github2.client import Github


logger = logging.getLogger(__name__)

class GitHubIssuesExtra( ScrumdoProjectExtra ):
  
  def __init__(self):
    print "GitHubIssuesExtra created"

  def getName(self):
    return "GitHub Issues"
    
  def getLogo(self):
    return settings.STATIC_URL + "extras/github-logo.png"
    
  
  def getSlug(self):
    "Returns a version of the name consisting of only letters, numbers, or dashes"
    return "github_issues"
      
  
  def getDescription(self):
    "Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user."    
    return "Create ScrumdDo stories for any open GitHub issue.  Push ScrumDo stories to GitHub issues."
    
  def doProjectConfigration( self, request, project ):
    """Handles a request to do configuration for the github_issues extra.
       This displays a form asking for credentials / repository information,
       then saves that with the saveConfiguration() api in ScrumdoProjectExtra base
       class.  After a successful configuration, we redirect back to the extras page.
       (Should each extra be responsible for that?)"""
       
    configuration = self.getConfiguration( project.slug )    
    if request.method == "POST":
      form = forms.GitHubIssuesConfig( request.POST )
      if form.is_valid():
        configuration = form.cleaned_data
        self.saveConfiguration( project.slug, configuration )        
        return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project.slug}))
    else:  
      form = forms.GitHubIssuesConfig(initial=configuration)
    return render_to_response("extras/github_issues/configure.html", {
        "project":project,
        "extra":self,
        "form":form
      }, context_instance=RequestContext(request))
    

  def associate( self, project):
    "called when an extra is first associated with a project."
    logger.info("Project associated with GitHubIssuesExtra")

  
  def unassociate( self, project):
    "called when an extra is removed from a project."
    logger.info("Project unassociated with GitHubIssuesExtra")
    
    
    
    
    
  def syncronizeProject( self, project ):
    configuration = self.getConfiguration( project.slug )   

    github = Github(username=configuration['username'], api_token=configuration['password'],requests_per_second=1)
    issues = github.issues.list(configuration['repository'], state="open")
    for issue in issues:
      print issue.title
    
    
    
