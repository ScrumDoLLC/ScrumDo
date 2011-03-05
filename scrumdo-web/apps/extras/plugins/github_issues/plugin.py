from extras.interfaces import ScrumdoProjectExtra
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import datetime
import forms
import logging

import sys, traceback

from extras.models import StoryQueue, SyncronizationQueue, ExternalStoryMapping
from extras.plugins.github_issues.github2.client import Github
                      
from projects.models import Story

logger = logging.getLogger(__name__)

class Plugin( ScrumdoProjectExtra ):     
  """ This Extra allows you to syncronize your GitHub issues with your ScrumDo stories. """
  
  def getName(self):                                                                    
    "Friendly name to display in the configuration options to the user."
    return "GitHub Issues"
    
  def getLogo(self):    
    return settings.STATIC_URL + "extras/github-logo.png"
      
  def getSlug(self):
    "Returns a version of the name consisting of only letters, numbers, or dashes"
    return "github_issues"
        
  def getDescription(self):
    "Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user."    
    return "Create ScrumdDo stories for any open GitHub issue.  Push ScrumDo stories to GitHub issues."
    
  def doProjectConfiguration( self, request, project ):
    """Handles a request to do configuration for the github_issues extra.
       This displays a form asking for credentials / repository information,
       then saves that with the saveConfiguration() api in ScrumdoProjectExtra base
       class.  After a successful configuration, we redirect back to the extras page.
       (Should each extra be responsible for that?)"""
           
    # The super class has a helper getConfiguration method that will return a dict of options.
    configuration = self.getConfiguration( project.slug )    
    if request.method == "POST":
      form = forms.GitHubIssuesConfig( request.POST )
      if form.is_valid():
        configuration = form.cleaned_data
        configuration["status"] = "Configuration Saved"
        
        # The super class has a helper saveConfiguration method that will save a 
        # dict of options for later retrieval by getConfiguration
        self.saveConfiguration( project.slug, configuration )        
        
        if configuration.get("upload"):
          # Need to queue an intial action to upload our project.
          self.manager.queueSyncAction(self.getSlug(), project, SyncronizationQueue.ACTION_INITIAL_SYNC)
          
        return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project.slug}))
    else:  
      form = forms.GitHubIssuesConfig(initial=configuration)
    return render_to_response("extras/github_issues/configure.html", {
        "project":project,
        "extra":self,
        "form":form
      }, context_instance=RequestContext(request))

  
  def storyDeleted( self, project, external_id, **kwargs):
    """Called when a story is deleted in a project that this extra is associated with.  """
    configuration = self.getConfiguration( project.slug )  

    if not configuration.get('delete'):          
      return # Not configured to delete stories.            

    repository = configuration.get('repository')
    logging.debug("Attempting to delete GitHub issue %s" % external_id)   
    github = kwargs.get( "github", Github(username=configuration.get('username'), api_token=configuration.get('password'),requests_per_second=1) )
    issue = github.issues.close( repository, external_id )        

        
  def storyCreated( self, project, story, **kwargs):
    """ Called when a new ScrumDo story is created. This plugin creates a GitHub issue if the upload option is enabled. """

    if self._getExternalLink( story ) != None:      
      # Already uploaded 
      return     

    configuration = self.getConfiguration( project.slug )  

    if not configuration.get('upload'):    
      # Not configured to upload new stories.
      return

    repository = configuration.get('repository')
    logging.debug("Attempting to create GitHub issue for story %d" % story.id)   
    github = kwargs.get( "github", Github(username=configuration.get('username'), api_token=configuration.get('password'),requests_per_second=1) )
    issue = github.issues.open( repository, story.summary, story.detail )
    link = ExternalStoryMapping( story=story,     
                                 extra_slug=self.getSlug(),
                                 external_id=issue.number,
                                 external_url="https://github.com/%s/issues/#issue/%d" % (repository, issue.number) )
    link.save()
    logging.info("GitHub issue #%d created for story %d" % (issue.number, story.id) )          
    
  def associate( self, project):
    "called when an extra is first associated with a project."
    logger.info("Project associated with GitHubIssuesExtra")
  
  def unassociate( self, project):
    "called when an extra is removed from a project."
    logger.info("Project unassociated with GitHubIssuesExtra")
    
  def getShortStatus(self, project):
    try:
      configuration = self.getConfiguration( project.slug )     
      return configuration.get("status")
    except:
      return "Not configured"
    
    
  def pullProject( self, project ):
    """ Pulls any new GitHub issues to Scrumdo, updates any existing
        Scrumdo stories that were associated with GitHub issues. """
    logging.debug("GitHubIssues::pullProject starting up.")
    configuration = self.getConfiguration( project.slug )   

    # The configuration view sets a download flag to true/false depending on user input.
    if not configuration.get("download"):
      logging.debug("Not set to download stories, aborting.")
      return
    
    try:
      logging.debug("Retrieving remote issues")
      github = Github(username=configuration.get('username'), api_token=configuration.get('password'),requests_per_second=1)
      issues = github.issues.list(configuration.get('repository'), state="open")
    except:
      logging.warn("Failed to retrieve remote GitHub issues for project %s" % project.slug)
      configuration["status"] = "Failed to load your GitHub issues"
      self.saveConfiguration( project.slug, configuration )      
      return
    
    logging.debug("Retrieved %d GitHub issues" % len(issues) )
    
    queue_stories = StoryQueue.objects.filter( project=project, extra_slug=self.getSlug() )
    logging.debug("%d stories already sitting in the story queue" % len(queue_stories) )
    project_stories = self._getStoriesInProjectAssociatedWithExtra( project )
    logging.debug("%d stories in the project associated with GitHub issues" % len(project_stories) )
    
    for issue in issues:
      story = self._getStory( issue.number, queue_stories, project_stories)
      if story == None:
        self._createStoryForIssue( issue, project , configuration.get('repository'))
      else:                                                      
        if story.summary != issue.title or story.detail != issue.body :
          logging.debug("Updating story %d." % story.id )
          story.summary=issue.title
          story.detail=issue.body
          story.save()
        
        
    
    configuration["status"] = "Syncronized with GitHub on " + str( datetime.date.today()  )
    logging.debug("pullProject complete, saving configuration.")
    self.saveConfiguration( project.slug, configuration )                        

  def initialSync( self, project):
    logging.debug("Performing initial GitHub issues syncronization.")
    configuration = self.getConfiguration( project.slug )   
    if configuration.get('upload'):
      try:
        self._initialUpload( project, configuration)
      except:                                                      
        logging.debug("Failed to upload stories.")
        traceback.print_exc(file=sys.stdout)
        configuration["status"] = "Syncronization failed to upload stories to GitHub on " + str( datetime.date.today()  )        
        self.saveConfiguration( project.slug, configuration )
        return
        
    self.pullProject(project)
    
  def storyUpdated( self, project, story , **kwargs):
    "Called when a story is updated in a project that this extra is associated with."    
    logging.debug("GitHub issues::storyUpdated")
    configuration = self.getConfiguration( project.slug )   

    # I think we should update stories if an external link exists, no matter how it got there.
    # # The configuration view sets a download flag to true/false depending on user input.
    # if not configuration.get("upload"):
    #   logging.debug("Not set to upload stories, aborting.")
    #   return                                  
    
    link = self._getExternalLink( story )
    
    if link == None:
      logging.debug("Story not associated with external story, aborting.")
      return
    
    # Grab the github client passed in kwargs, if none, create one.
    github = kwargs.get( "github", Github(username=configuration.get('username'), api_token=configuration.get('password'),requests_per_second=1) )                                                                        
    github.issues.edit( configuration.get('repository'), link.external_id, story.summary, story.detail )


  def storyStatusChange( self, project, story, **kwargs):
    logging.debug("GitHub issues::storyStatusChange")
    configuration = self.getConfiguration( project.slug )   

    # The configuration view sets a download flag to true/false depending on user input.
    if not configuration.get("upload"):
      logging.debug("Not set to upload stories, aborting.")
      return                                  
    
    link = self._getExternalLink( story )
    
    if link == None:
      logging.debug("Story not associated with external story, aborting.")
      return
    # Grab the github client passed in kwargs, if none, create one.
    github = kwargs.get( "github", Github(username=configuration.get('username'), api_token=configuration.get('password'),requests_per_second=1) )                                                                        
    
    if story.status == Story.STATUS_DONE:
      github.issues.close( configuration.get('repository'), link.external_id )
    else:
      # All other scrumdo statuses map to open on github issues.
      github.issues.reopen( configuration.get('repository'), link.external_id )
      


  def _createStoryForIssue( self, issue, project , repository):
    logging.debug("Attempting to create new StoryQueue object for issue %d" % issue.number )
    try:            
      story = StoryQueue.objects.get( project=project, external_id=issue.number)
      # Odd, it already exists!
      story.summary=issue.title
      story.detail=issue.body      
    except StoryQueue.DoesNotExist:    
      story = StoryQueue(project=project, 
                       extra_slug=self.getSlug(),
                       external_id=issue.number,
                       external_url="https://github.com/%s/issues/#issue/%d" % (repository, issue.number),
                       summary=issue.title,
                       detail=issue.body )
    story.save()

  def _getStoriesInProjectAssociatedWithExtra(self, project):
    rv = []
    for story in project.stories.all():
      if self._getExternalLink( story ) != None:
        rv.append( story )

    return rv                                                           

  def _getStory( self, external_id, queue_stories, project_stories ):   
    """ Pass in an external id, list of stories in the queue, and a list of stories in the project, and will return the story if the it exists in either list. """
    story = self._getStoryFromQueue( external_id, queue_stories)
    if story != None:
      return story
    return self._getStoryFromProject( external_id, project_stories )
    
  def _initialUpload(self, project, configuration):
    configuration = self.getConfiguration( project.slug )
    github = Github(username=configuration.get('username'), api_token=configuration.get('password'),requests_per_second=1)
    for story in project.stories.all():
      self.storyCreated(project, story, github=github)

  # TODO - is this general enough to bump up to the super class?
  def _getExternalLink( self, story ):
    """ Searches for the ExternalStoryMapping that is associated with this extra and returns it.
        returns None if it's not found. """
    for link in story.external_links.all():
      if link.extra_slug == self.getSlug():
        return link
    return None
    
  def _getStoryFromProject(self, external_id, project_stories ):
    """ Returns the story from the list with the given external ID for this extra. """
    for project_story in project_stories:
      for link in project_story.external_links.all():
        if link.extra_slug == self.getSlug() and str(link.external_id)==str(external_id):
          return project_story
    return None
      
  def _getStoryFromQueue(self, external_id, queue_stories ):                         
    """ Returns the story from the list of StoryQueue objects with the given external id. """
    for queue_story in queue_stories:
      if queue_story.extra_slug == self.getSlug() and int(queue_story.external_id)==external_id:
        return queue_story
    return None
      
