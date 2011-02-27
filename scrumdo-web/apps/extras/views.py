from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from manager import manager
from projects.access import *
from projects.models import Story
import logging

from models import StoryQueue, ExternalStoryMapping
logger = logging.getLogger(__name__)

import signals



def project_extra_callback(request, extra_slug, project_slug):
  pass
  
  

  
def import_story(request, project_slug, queue_id):
  logger.debug("Adding story from StoryQueue")
  project = get_object_or_404( Project, slug=project_slug )
  write_access_or_403(project, request.user )  
  story = StoryQueue.objects.get(id=queue_id)  
  if story.project != project:
    # Shenanigans here!
    raise PermissionDenied()
  
  # TODO (Useability):
  #    What should rank be set at to make the most sense?  
  new_story = Story(project=project, rank=0, 
                    local_id=project.getNextId(), 
                    summary=story.summary,
                    detail=story.detail,
                    extra_1=story.extra_1,
                    extra_2=story.extra_2,
                    extra_3=story.extra_3,
                    status=story.status,
                    points=story.points,
                    iteration = project.get_default_iteration(),
                    creator = request.user
                    )  
  new_story.save()
  mapping = ExternalStoryMapping(story=new_story,
                                 external_id=story.external_id,
                                 external_url=story.external_url,
                                 extra_slug=story.extra_slug)
  mapping.save()
  request.user.message_set.create(message="Story imported.")
  
  story.delete() # delete the story queue object since we just imported it.
  
  signals.story_imported.send( sender=request, story=new_story, user=request.user )
  
  return HttpResponseRedirect(reverse("story_queue_url", kwargs={'project_slug':project_slug} )) #story_queue(request,project_slug)
  
  
def story_queue( request, project_slug):
  project = get_object_or_404( Project, slug=project_slug )
  write_access_or_403(project, request.user )  
  return render_to_response("extras/story_queue.html", {
      "project":project,
    }, context_instance=RequestContext(request))  

def syncronize_extra(request, project_slug, extra_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  manager.syncronizeExtra( extra_slug, project )
  return HttpResponse("OK")

def enable_extra( request, project_slug, extra_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  manager.enableExtra(project,extra_slug)
  return HttpResponseRedirect(reverse("configure_extra_url",kwargs={'project_slug':project_slug, "extra_slug":extra_slug}))

def disable_extra( request, project_slug, extra_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  manager.disableExtra(project,extra_slug)  
  return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project_slug}))

def configure_extra( request, project_slug, extra_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  extra = manager.getExtra( extra_slug )
  if extra != None:
    return extra.doProjectConfiguration(request, project)
  return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project_slug}))

def project_extras(request, project_slug):
  project = get_object_or_404( Project, slug=project_slug )
  admin_access_or_403(project, request.user )  
  return render_to_response("extras/project_extras.html", {
      "project":project,
      "extras":manager.getExtraConfigs(project)
    }, context_instance=RequestContext(request))

def project_extra_options( request, extra_slug, project_slug):
  pass