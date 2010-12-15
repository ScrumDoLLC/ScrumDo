from django.contrib.sites.models import Site


# Interface that 'Extras' for the scrumdo site must implement.  Extras usually 
# implement a connection to a third party service.
class ScrumdoExtra:
    
  # Returns a user-friendly version of the name of this extra.  Generally should be just a couple words long.
  def getName(self):
    raise NotImplementedError("ScrumdoExtra subclasses must implement getName()")

  # Returns a URL to a logo that can be used on the config page.
  def getLogo(self):
    raise NotImplementedError("ScrumdoExtra subclasses must implement getLogo()")
        
  # Returns a version of the name consisting of only letters, numbers, or dashes
  # Max length, 25 chars
  def getSlug(self):
    raise NotImplementedError("ScrumdoExtra subclasses must implement getSlug()")
      
  # Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user.
  def getDescription(self):
    raise NotImplementedError("ScrumdoExtra subclasses must implement getDescription()")
  
  
    
  
# Interface for extras that should be associated with a project.  
class ScrumdoProjectExtra( ScrumdoExtra ):

  # called when an extra is first associated with a project.
  def associate( self, project):
    raise NotImplementedError("ScrumdoProjectExtra subclasses must implement initialize()")

  # called when an extra is removed from a project.
  def unassociate( self, project):
    raise NotImplementedError("ScrumdoProjectExtra subclasses must implement unassociate()")
    
    
  # Should return a string representing the current status that this extra has for a given project.  
  # Examples: 'Successfully syncronized on 1/1/2010' or 'Syncronization last failed' or 'Everything OK' 
  def getShortStatus( self,  project ):
    raise NotImplementedError("ScrumdoProjectExtra subclasses must implement getShortStatus()")

  # Should return a django style response that handles any configuration that this extra may need.
  def doProjectConfigration( self, request, project ):
    raise NotImplementedError("ScrumdoProjectExtra subclasses must implement doProjectConfigration()")

  # Should cause a full push/pull syncronization of this extra with whatever external source 
  # there is.  This will be called on a scheduled basis for all active projects.  The project 
  # parameter be an apps.projects.models.Project object.    
  def syncronizeProject( self, project ):
    pass

  # Every extra gets a URL that external services can POST to.  This should handle those requests.
  def externalHook( self, request ):
    pass

  # Called when a story is updated in a project that this extra is associated with.
  def storyUpdated( self, project, story ):
    pass

  # Called when a story is deleted in a project that this extra is associated with.
  def storyDeleted( self, project, story):
    pass

  # Called when a story is created in a project that this extra is associated with.
  def storyCreated( self, project, story):
    pass
  
  # Returns where an external site can post to, to give this extra information.
  # You probably don't want to change this in subclasses.
  def getExtraHookURL( self, project ):
    current_site = Site.objects.get_current()
    return "http://" + current_site.domain + "/extras/" + self.getSlug() + "/project/" +  project.slug + "/hook"
    



# Organization based Extras are not yet ready to use...
# 
# class ScrumdoOrganizationExtra( ScrumdoExtra ):
#   "Interface for extras that should be associated with an Organization"
# 
#   def syncronizeOrganization( organization ):
#     "Should cause a full push/pull syncronization of this extra with whatever external source \
#      there is.  This will be called on a scheduled basis for all active projects.  The organization \
#      parameter be an apps.projects.models.Project object."
# 
#   def doOrganizationConfigration(request, organization ):
#     "Should return a django style response that handles any configuration that this extra may need."
# 
#   def getShortStatus( organization ):
#     "Should return a string representing the current status that this extra has for a given project.  \
#     Examples: 'Successfully syncronized on 1/1/2010' or 'Syncronization last failed' or 'Everything OK' "
# 
# 
#   def teamUpdated( organization, team ):
#     "Called when a team is updated in a organization that this extra is associated with."
# 
#   def teamDeleted( organization, team):
#     "Called when a team is deleted in a organization that this extra is associated with."
# 
#   def teamCreated( organization, team):
#     "Called when a team is created in a organization that this extra is associated with."
#     
# 
#   def projectUpdated( organization, project ):
#     "Called when a project is updated in a organization that this extra is associated with."
# 
#   def projectDeleted( organization, project):
#     "Called when a project is deleted in a organization that this extra is associated with."
# 
#   def projectCreated( organization, project):
#     "Called when a project is created in a organization that this extra is associated with."

