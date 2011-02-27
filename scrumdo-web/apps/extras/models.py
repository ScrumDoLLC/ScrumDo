from datetime import datetime, date
from django.db import models
import time

from django.core.urlresolvers import reverse
from projects.models import Project, Iteration, Story, Task


# Determines which extras are active for which projects.
# The configuration stores a json object of configuration options to make storing that sort of
# data easier on the extra.
class ProjectExtraMapping( models.Model ):
  project = models.ForeignKey(Project, related_name="extras")
  extra_slug = models.CharField( "extra_slug" , max_length=25)
  configuration = models.TextField( )  


# When an extra imports stories, it should put them into the story queue instead of directly into Story objects.
# this way, the user will be presented with a list of stories that they can choose to use or not from all of their
# external sources.
#
# After a story is imported, the extra should feel free to directly update it on syncronizations.
class StoryQueue( models.Model ):
  project = models.ForeignKey(Project, related_name="story_queue")
  extra_slug = models.CharField( "extra_slug" , max_length=25)
  
  external_id = models.CharField( max_length=40)
  external_url = models.CharField( max_length=256, blank=True , null=True)
  imported_on = models.DateTimeField( default=datetime.now)
  modified = models.DateTimeField( default=datetime.now) 
    
  summary = models.TextField( )  
  detail = models.TextField( blank=True )
  points = models.CharField('points', max_length=3, default="?" ,blank=True)
  status = models.IntegerField( max_length=2, choices=Story.STATUS_CHOICES, default=1 )
  extra_1 = models.TextField( blank=True , null=True)
  extra_2 = models.TextField( blank=True , null=True)
  extra_3 = models.TextField( blank=True , null=True)

class SyncronizationQueue( models.Model ):
  ACTION_SYNC_REMOTE = 1
  ACTION_STORY_UPDATED = 2
  ACTION_STORY_DELETED = 3
  ACTION_STORY_CREATED = 4
  ACTION_INITIAL_SYNC = 5
  ACTION_STORY_STATUS_CHANGED = 6
  ACTION_TASK_UPDATED = 7
  ACTION_TASK_DELETED = 8
  ACTION_TASK_CREATED = 9
  ACTION_TASK_STATUS_CHANGED = 10
  ACTION_STORY_IMPORTED = 11
  
  ACTION_CHOICES = (
      (1, "SYNC_REMOTE"),
      (2, "STORY_UPDATED"),
      (3, "STORY_DELETED"),
      (4, "STORY_CREATED"),
      (5, "INITIAL_SYNC"),
      (6, "ACTION_STORY_STATUS_CHANGED"),
      (7, "ACTION_TASK_UPDATED"),
      (8, "ACTION_TASK_DELETED"),
      (9, "ACTION_TASK_CREATED"),
      (10, "ACTION_TASK_STATUS_CHANGED"),
      (11, "ACTION_STORY_IMPORTED")   )
  
  project = models.ForeignKey(Project)
  story = models.ForeignKey(Story, null=True, related_name="sync_queue")
  task = models.ForeignKey(Task, null=True, related_name="sync_queue")
  extra_slug = models.CharField(  max_length=25)
  action = models.IntegerField( max_length=2, choices=ACTION_CHOICES )
  queue_date = models.DateTimeField( default=datetime.now)
  external_id = models.CharField( max_length=40 , null=True)
  
  
class ExternalStoryMapping( models.Model ):
  """ When a story is related to external, third party sites, this gives a way of associating a reference to that other site.
      For instance, we store the GitHub Issue ID for any story that was imported from GitHub issues, or exported to it.
      This way, we can map them back and forth for syncronization purposes.
  """
  story = models.ForeignKey(Story, related_name="external_links")
  external_id = models.CharField( max_length=40 )
  external_url = models.CharField( max_length=256, blank=True , null=True)
  extra_slug = models.CharField( max_length=20 )
  
class ExternalTaskMapping( models.Model ):
    """ When a task is related to external, third party sites, this gives a way of associating a reference to that other site."""
    task = models.ForeignKey(Task, related_name="external_links")
    external_id = models.CharField( max_length=40 )
    external_url = models.CharField( max_length=256, blank=True , null=True)
    extra_slug = models.CharField( max_length=20 )  

  
class ExtraConfiguration( models.Model ):
  extra_slug = models.CharField( "extra_slug" , max_length=25)
  project_slug = models.CharField( "project_slug" , max_length=55)
  configuration_pickle = models.TextField( blank=True )