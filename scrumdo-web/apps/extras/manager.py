from django.conf import settings
import logging
import sys, traceback

import projects.signals as project_signals
import projects.limits as project_limits
import extras.signals as extras_signals

from models import ProjectExtraMapping, ExtraConfiguration, SyncronizationQueue , ExternalStoryMapping, StoryQueue, ExternalTaskMapping

logger = logging.getLogger(__name__)

class ExtrasManager:
  """
    Class to manage our list of extras.
  """
  
  def getExtras(self):
    return self.extras.values()
    
  def getExtra( self, slug ):
    return self.extras[ slug ]
    
  # TODO (performance) - do some actions invalidate others?  For instance, if we have an ACTION_STORY_UPDATED sitting in the queue, and
  #        a ACTION_STORY_DELETED action comes through, can we delete the ACTION_STORY_UPDATED?
  #        what about duplicate actions?  Can we ignore those?
  def queueSyncAction( self, extra_slug, project, action, **kwargs):
      logger.debug("Queuing a syncronization action %d, %s, %s" % (action,project.slug,extra_slug))
      queueObject = SyncronizationQueue( project=project, extra_slug=extra_slug, action=action)
      queueObject.story = kwargs.get("story",None)     
      queueObject.task = kwargs.get("task",None)
      if queueObject.task == None:
          try:          
              mapping = ExternalStoryMapping.objects.get(story=queueObject.story,extra_slug=extra_slug)
              queueObject.external_id = mapping.external_id
          except:
              pass      
      else:
          try:
              mapping = ExternalTaskMapping.objects.get(task=queueObject.task,extra_slug=extra_slug)
              queueObject.external_id = mapping.external_id
          except:
              pass
      queueObject.save()
    
  def queueSyncActions(self, project, action, **kwargs):      
      for mapping in project.extras.all():
          self.queueSyncAction( mapping.extra_slug, project, action, **kwargs)
  
  def getExtraConfigs( self , project):
      extras = self.extras.values();
      rv = []
      for extra in extras:
          if extra.isPremium() and project.organization==None and not project_limits.personal_extra_limit.increaseAllowed(project=project):
              continue
          if extra.isPremium() and project.organization!=None and not project_limits.org_extra_limit.increaseAllowed(organization=project.organization):
              continue
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
    
    story_mappings = ExternalStoryMapping.objects.filter( story__project=project, extra_slug=extra_slug )
    for story_mapping in story_mappings:
      story_mapping.delete()
    
    story_queue = StoryQueue.objects.filter( project=project, extra_slug=extra_slug)
    for queue_item in story_queue:
      queue_item.delete()
      
    extra = self.getExtra(extra_slug)
    extra.unassociate( project )
      

  def is_extra_enabled( self, project, extra_slug ):
    return ProjectExtraMapping.objects.filter( project=project, extra_slug=extra_slug).count() > 0
  
  def onStoryUpdated(self, sender, **kwargs):
      story = kwargs["story"]      
      logger.debug("extras.ExtrasManager::onStoryUpdated(story=%d)" % ( story.id) )           
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_STORY_UPDATED , story=story)
    
  def onStoryStatusChanged(self, sender, **kwargs):             
      story = kwargs["story"]                                 
      logger.debug("extras.ExtrasManager::onStoryStatusChanged(project=%s, story=%d)" % (story.project.slug, story.id))
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_STORY_STATUS_CHANGED , story=story)

  def onStoryDeleted(self, sender, **kwargs):                                                                  
      story = kwargs["story"]      
      logger.debug("extras.ExtrasManager::onStoryDeleted(project=%s, story=%d)" % (story.project.slug, story.id))    
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_STORY_DELETED , story=story)

  def onStoryCreated(self, sender, **kwargs):                   
      story = kwargs["story"]      
      logger.debug("extras.ExtrasManager::onStoryCreated(project=%s, story=%d)" % (story.project.slug, story.id))
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_STORY_CREATED , story=story)
  
  def onTaskUpdated(self, sender, **kwargs):
      task = kwargs["task"]
      story = task.story
      logger.debug("extras.ExtrasManager::onTaskUpdated(story=%d)" % ( story.id) )           
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_TASK_UPDATED , story=story, task=task)

  def onTaskStatusChanged(self, sender, **kwargs):             
      task = kwargs["task"]
      story = task.story
      logger.debug("extras.ExtrasManager::onTaskStatusChanged(project=%s, story=%d)" % (story.project.slug, story.id))
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_TASK_STATUS_CHANGED , story=story, task=task)

  def onTaskDeleted(self, sender, **kwargs):                                                                  
      task = kwargs["task"]
      story = task.story
      logger.debug("extras.ExtrasManager::onTaskDeleted(project=%s, task=%s)" % (story.project.slug, task))    
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_TASK_DELETED , story=story, task=task)

  def onTaskCreated(self, sender, **kwargs):                   
      task = kwargs["task"]
      story = task.story
      logger.debug("extras.ExtrasManager::onTaskCreated(project=%s, story=%d)" % (story.project.slug, story.id))
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_TASK_CREATED , story=story, task=task)
      
  def onStoryImported(self, sender, **kwargs):
      story = kwargs["story"]
      logger.debug("extras.ExtrasManager::onStoryCreated(project=%s, story=%d)" % (story.project.slug, story.id))
      self.queueSyncActions( story.project, SyncronizationQueue.ACTION_STORY_IMPORTED , story=story)
      

  def __init__(self, extras_settings):
    manager = self
    self.extras = {}        
    project_signals.story_updated.connect(self.onStoryUpdated, dispatch_uid="extra_signal_hookup")    
    project_signals.story_status_changed.connect(self.onStoryStatusChanged, dispatch_uid="extra_signal_hookup")    
    project_signals.story_deleted.connect(self.onStoryDeleted, dispatch_uid="extra_signal_hookup")    
    project_signals.story_created.connect(self.onStoryCreated, dispatch_uid="extra_signal_hookup")    
    
    project_signals.task_updated.connect(self.onTaskUpdated, dispatch_uid="extra_signal_hookup")    
    project_signals.task_status_changed.connect(self.onTaskStatusChanged, dispatch_uid="extra_signal_hookup")    
    project_signals.task_deleted.connect(self.onTaskDeleted, dispatch_uid="extra_signal_hookup")    
    project_signals.task_created.connect(self.onTaskCreated, dispatch_uid="extra_signal_hookup")
    
    extras_signals.story_imported.connect( self.onStoryImported, dispatch_uid="extra_signal_hookup")
        
    for extra in extras_settings:      
      extra_class = get_class( extra )
      extra = extra_class()
      extra.manager = self
      self.extras[ extra.getSlug() ] = extra
      
def get_class( kls ):
    return getattr(__import__( kls , {}, {}, ['Plugin']), 'Plugin')

    
manager = ExtrasManager( settings.SCRUMDO_EXTRAS )  