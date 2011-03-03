#!/usr/bin/env python

# ScrumDo - Agile/Scrum story management web application 
# Copyright (C) 2011 ScrumDo LLC
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA



# This script handles running the extra's syncronization logic.
# You should set this up on some sort of scheduled basis.  The
# scrumdo.com website runs it once a minute.

import sys
from datetime import date, timedelta

from apps.projects.models import Project, Iteration, Story, PointsLog
from apps.extras.models import ProjectExtraMapping, SyncronizationQueue
from apps.extras.manager import manager

import logging
import sys, traceback
import getopt

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
  args = "pull"
  def handle(self, *args, **options):
    options, remainder = getopt.getopt(sys.argv[1:], 'p', ['pull'])
    
    for arg in args:        
        if arg == "pull":            
            if len(remainder) == 3:
                setUpPullQueue( project_slug=remainder[2] )
            else:
                setUpPullQueue()
                return
    processQueue()


def setUpPullQueue( **kwargs ):
    logging.info("Setting up queue to pull all projects next time.")
    project_slug = kwargs.get("project_slug",None)
    mappings = ProjectExtraMapping.objects.all()
    for mapping in mappings:
        if project_slug==None or project_slug==mapping.project.slug:      
            qItem = SyncronizationQueue(project=mapping.project, extra_slug=mapping.extra_slug, action=SyncronizationQueue.ACTION_SYNC_REMOTE) 
            qItem.save()


def processQueue():    
  queue = SyncronizationQueue.objects.all()
  for queueItem in queue:
    # In case a second invocation of this script occurs while it's running, we don't want
    # to re-process any items...
    queueItem.delete()
    pass
    
  for queueItem in queue:
    try:
      project = queueItem.project
      story = queueItem.story
      task = queueItem.task
      action = queueItem.action
      extra_slug = queueItem.extra_slug
      action = queueItem.action
      external_id = queueItem.external_id
      
      extra = manager.getExtra( extra_slug )
      
      if action == SyncronizationQueue.ACTION_SYNC_REMOTE:
          extra.pullProject(project)        
      elif action == SyncronizationQueue.ACTION_STORY_UPDATED:
          extra.storyUpdated(project,story)
      elif action == SyncronizationQueue.ACTION_STORY_DELETED:
          extra.storyDeleted(project,external_id)
      elif action == SyncronizationQueue.ACTION_STORY_CREATED:
          extra.storyCreated(project,story)    
      elif action == SyncronizationQueue.ACTION_STORY_STATUS_CHANGED:
          extra.storyStatusChange(project, story)
      elif action == SyncronizationQueue.ACTION_INITIAL_SYNC:
          extra.initialSync( project )
      elif action == SyncronizationQueue.ACTION_TASK_UPDATED:
          extra.taskUpdated(project, task)
      elif action == SyncronizationQueue.ACTION_TASK_DELETED:
          extra.taskDeleted(project, external_id)
      elif action == SyncronizationQueue.ACTION_TASK_CREATED:
          extra.taskCreated(project, task)
      elif action == SyncronizationQueue.ACTION_TASK_STATUS_CHANGED:
          extra.taskStatusChange(project, task)
      elif action == SyncronizationQueue.ACTION_STORY_IMPORTED:
          extra.storyImported(project, story)
    except RuntimeError:                                                 
      logger.error("RuntimeError occured while processing a syncronization queue item.")
      traceback.print_exc(file=sys.stdout)
    except:
      logger.error("Error occured while processing a syncronization queue item.") 
      traceback.print_exc(file=sys.stdout)
    
    


if __name__ == "__main__":
    main()
