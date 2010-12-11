from extras.interfaces import ScrumdoProjectExtra
from django.shortcuts import render_to_response
import logging

logger = logging.getLogger(__name__)

class GitHubIssuesExtra( ScrumdoProjectExtra ):

  def __init__(self):
    print "GitHubIssuesExtra created"

  def getName(self):
    return "GitHub Issues"
    
  # Returns a version of the name consisting of only letters, numbers, or dashes
  def getSlug(self):
    return "github-issues"
      
  # Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user.
  def getDescription(self):
    return "This Extra can create ScrumdDo stories for any uncompleted GitHub issue.  It is also capable of pushing ScrumDo stories as GitHub issues."
    
  # Should return a django style response that handles any configuration that this extra may need.
  def doProjectConfigration( self, request, project ):
    return 
    
  # called when an extra is first associated with a project.
  def associate( self, project):
    logger.info("Project associated with GitHubIssuesExtra")

  # called when an extra is removed from a project.
  def unassociate( self, project):
    logger.info("Project unassociated with GitHubIssuesExtra")