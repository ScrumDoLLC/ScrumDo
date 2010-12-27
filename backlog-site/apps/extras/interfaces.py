from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from extras.models import ExtraConfiguration
import base64
import pickle



class ScrumdoExtra:
  """ Interface that 'Extras' for the scrumdo site must implement.  Extras usually 
      implement a connection to a third party service. """
  
  def getName(self):
    "Returns a user-friendly version of the name of this extra.  Generally should be just a couple words long."    
    raise NotImplementedError("ScrumdoExtra subclasses must implement getName()")

  
  def getLogo(self):
    "Returns a URL to a logo that can be used on the config page."
    raise NotImplementedError("ScrumdoExtra subclasses must implement getLogo()")
        
  def getSlug(self):
    """ Returns a version of the name consisting of only letters, numbers, or dashes
        Max length, 25 chars    """
    raise NotImplementedError("ScrumdoExtra subclasses must implement getSlug()")
      
  
  def getDescription(self):
    " Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user. "
    raise NotImplementedError("ScrumdoExtra subclasses must implement getDescription()")
    
  # TODO (performance) - Probably want to memcache the configurations for a short period of time.
  def getConfiguration(self, project_slug ):
    """ Gets a configuration object (usually a dictionary) from the ExtraConfiguration table. """
    try:
      config = ExtraConfiguration.objects.get( extra_slug=self.getSlug(), project_slug=project_slug)
    except ObjectDoesNotExist:
      return {}
    return pickle.loads( base64.decodestring(config.configuration_pickle) )
    
  def saveConfiguration(self, project_slug, configuration_object ):
    """ Saves a configuration object (usually a dictionary) to the ExtraConfiguration table. 
        configuration_object must be pickleable """
        
    try:
      config = ExtraConfiguration.objects.get( extra_slug=self.getSlug(), project_slug=project_slug)
    except ObjectDoesNotExist:
      config = ExtraConfiguration( project_slug=project_slug, extra_slug=self.getSlug() )

    config.configuration_pickle = base64.encodestring( pickle.dumps( configuration_object ) )
    config.save()
      

  

class ScrumdoProjectExtra( ScrumdoExtra ):
  "Base calss for extras that should be associated with a project.  "
    
  
  def associate( self, project):
    "called when an extra is first associated with a project."
    pass


  
  def unassociate( self, project):
    "called when an extra is removed from a project."
    pass
    
    
  def getShortStatus( self,  project ):
    """ Should return a string representing the current status that this extra has for a given project.  
        Examples: 'Successfully syncronized on 1/1/2010' or 'Syncronization last failed' or 'Everything OK' """
    raise NotImplementedError("ScrumdoProjectExtra subclasses must implement getShortStatus()")

  
  def doProjectConfigration( self, request, project ):
    """ Should return a django style response that handles any configuration that this extra may need. """
    raise NotImplementedError("ScrumdoProjectExtra subclasses must implement doProjectConfigration()")


  def pushProject( self, project):
    """ Should cause a full push syncronization of this extra to whatever external source 
        there is.  This will be only be called on on rare events (such as an initial configuraiton
        of an extra, or on a forced sync of the extra) """
    pass
        
        
  def pullProject( self, project ):
    """ Should cause a full pull syncronization of this extra from whatever external source 
        there is.  This will be called on a scheduled basis for all active projects.  The project 
        parameter be an apps.projects.models.Project object.    """    
    pass

  
  def externalHook( self, request ):
    "Every extra gets a URL that external services can POST to.  This should handle those requests."
    pass

  
  def storyUpdated( self, project, story ):
    "Called when a story is updated in a project that this extra is associated with."
    pass
  
  def storyDeleted( self, project, story):
    "Called when a story is deleted in a project that this extra is associated with."
    pass

  
  def storyCreated( self, project, story):
    "Called when a story is created in a project that this extra is associated with."
    pass
  
  def getExtraHookURL( self, project ):
    """ Returns where an external site can post to, to give this extra information.
        You probably don't want to change this in subclasses. """
    
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

