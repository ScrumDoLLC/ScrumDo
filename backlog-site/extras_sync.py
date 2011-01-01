#!/usr/bin/env python

# This script handles running the extra's syncronization logic.
# You should set this up on some sort of scheduled basis.  The
# scrumdo.com website runs it once a minute.

import sys
from datetime import date, timedelta

from os.path import abspath, dirname, join

try:
    import pinax
except ImportError:
    sys.stderr.write("Error: Can't import Pinax. Make sure you are in a virtual environment that has Pinax installed or create one with pinax-boot.py.\n")
    sys.exit(1)

from django.conf import settings
from django.core.management import setup_environ, execute_from_command_line

try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from apps.projects.models import Project, Iteration, Story, PointsLog
from apps.extras.models import ProjectExtraMapping, SyncronizationQueue
from apps.extras.manager import manager

import logging
import sys, traceback
import getopt


logger = logging.getLogger(__name__)

def main():         
  options, remainder = getopt.getopt(sys.argv[1:], 'p', ['pull'])
  for opt, arg in options:
      if opt in ('-p', '--pull'):
          setUpPullQueue()
          return
  processQueue()


def setUpPullQueue():
  logging.info("Setting up queue to pull all projects next time.")
  mappings = ProjectExtraMapping.objects.all()
  for mapping in mappings:
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
      action = queueItem.action
      extra_slug = queueItem.extra_slug
      action = queueItem.action
      external_id = queueItem.action
      
      extra = manager.getExtra( extra_slug )
      
      if action == SyncronizationQueue.ACTION_SYNC_REMOTE:
        extra.pullProject(project)        
      elif action == SyncronizationQueue.ACTION_STORY_UPDATED:
        extra.storyUpdated(project,story)
      elif action == SyncronizationQueue.ACTION_STORY_DELETED:
        extra.storyDeleted(project,external_id)
      elif action == SyncronizationQueue.ACTION_STORY_CREATED:
        extra.storyCreated(project,story)
      elif action == SyncronizationQueue.ACTION_INITIAL_SYNC:
        extra.initialSync( project )
    except RuntimeError:                                                 
      logger.error("RuntimeError occured while processing a syncronization queue item.")
      traceback.print_exc(file=sys.stdout)
    except:
      logger.error("Error occured while processing a syncronization queue item.") 
      traceback.print_exc(file=sys.stdout)
    
    


if __name__ == "__main__":
    main()
