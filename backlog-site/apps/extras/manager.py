from django.conf import settings
from models import ProjectExtraMapping, ExtraConfiguration, SyncronizationQueue





class ExtrasManager:
  """
    Small class to manage our list of extras.
  """
  
  def getProjectConfig( self , project):
    pass
  
  def getExtras(self):
    return self.extras.values()
    
  def getExtra( self, slug ):
    return self.extras[ slug ]
    
  # TODO - do some actions invalidate others?  For instance, if we have an ACTION_STORY_UPDATED sitting in the queue, and
  #        a ACTION_STORY_DELETED action comes through, can we just delete the ACTION_STORY_UPDATED?
  def queueSyncAction( self, extra_slug, project, action, **kwargs):
    queueObject = SyncronizationQueue( project=project, extra_slug=extra_slug, action=action)
    queueObject.story = kwargs.get("story",None)
    queueObject.save()
    
    
  def getExtraConfigs( self , project):
    extras = self.extras.values();
    rv = []
    for extra in extras:
      config = {}
      config["extra"] = extra
      config["enabled"] = self.is_extra_enabled(project, extra.getSlug() )
      config["status"] = extra.getShortStatus( project )
      rv.append( config )
    return rv

  def syncronizeExtra(self, extra_slug, project ):
    extra = self.getExtra( extra_slug )
    extra.pullProject( project )

  def enableExtra( self, project, extra_slug ):
    config = ProjectExtraMapping( project=project, extra_slug=extra_slug )
    config.save()
    extra = self.getExtra(extra_slug)
    extra.associate( project )

  def disableExtra( self, project, extra_slug ):
    mappings = ProjectExtraMapping.objects.filter( project=project, extra_slug=extra_slug)
    for mapping in mappings:
      mapping.delete()

    configs = ExtraConfiguration.objects.filter( extra_slug=extra_slug, project_slug=project.slug)
    for config in configs:
      config.delete()
      
    extra = self.getExtra(extra_slug)
    extra.unassociate( project )
      

  def is_extra_enabled( self, project, extra_slug ):
    return ProjectExtraMapping.objects.filter( project=project, extra_slug=extra_slug).count() > 0

  def __init__(self, extras_settings):
    manager = self
    self.extras = {}
    for extra in extras_settings:      
      extra_class = get_class( extra )
      extra = extra_class()
      extra.manager = self
      self.extras[ extra.getSlug() ] = extra
      
def get_class( kls ):
  parts = kls.split('.')
  module = ".".join(parts[:-1])
  m = __import__( module )
  for comp in parts[1:]:
      m = getattr(m, comp)            
  return m
    
    
manager = ExtrasManager( settings.SCRUMDO_EXTRAS )  