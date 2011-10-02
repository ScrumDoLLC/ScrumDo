from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.core.paginator import Paginator, InvalidPage

from manager import manager
from projects.access import *
from projects.models import Story, Iteration
import logging

from models import StoryQueue, ExternalStoryMapping
logger = logging.getLogger(__name__)

import signals
import json


def project_extra_callback(request, extra_slug, project_slug):
    pass



@login_required
def import_stories(request, project_slug):
    logger.debug("Adding story from StoryQueue")
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user )
    queue_ids = str(request.POST.get("stories","")).split(",")
    iteration = project.get_default_iteration()
    count = 0
    
    for queue_id in queue_ids:    
        try:
            story = StoryQueue.objects.get(id=queue_id)
        except:
            continue

        if story.project != project:
            # Shenanigans here!
            raise PermissionDenied()

        new_story = Story(project=project, rank=0,
                          local_id=project.getNextId(),
                          summary=story.summary,
                          detail=story.detail,
                          extra_1=story.extra_1,
                          extra_2=story.extra_2,
                          extra_3=story.extra_3,
                          status=story.status,
                          points=story.points,
                          iteration = iteration,
                          creator = request.user
                          )
        new_story.save()
        logger.debug("Added story %d" % new_story.id)
        mapping = ExternalStoryMapping(story=new_story,
                                       external_id=story.external_id,
                                       external_url=story.external_url,
                                       extra_slug=story.extra_slug)
        mapping.save()
        story.delete() # delete the story queue object since we just imported it.
        signals.story_imported.send( sender=request, story=new_story, story_queue=story, user=request.user )
        count+=1
    
    return HttpResponse( "%d imported" % count )


@login_required
def ignore_stories(request, project_slug):
    logger.debug("Ignoring story from StoryQueue")
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user )
    queue_ids = str(request.POST.get("stories","")).split(",")
    count = 0

    for queue_id in queue_ids:    
        try:
            story = StoryQueue.objects.get(id=queue_id)
        except:
            continue

        if story.project != project:
            # Shenanigans here!
            raise PermissionDenied()

        story.archived = not story.archived
        story.save()
        count+=1

    return HttpResponse( "%d ignored" % count )

@login_required
def queued_stories(request, project_slug, page):
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user )    
    queue = project.story_queue.all().order_by("-imported_on")
    page = int(page) 
    
    if request.GET.get("archived","false") == "false":
        queue = queue.filter(archived=False)
    
    p = Paginator(queue, 20)
    if page > p.num_pages:
        page = p.num_pages
    if page < 1:
        page = 1
    pg = p.page( page )
    stories = pg.object_list
    
    
    return render_to_response("extras/story_queue_list.html", {
        "project":project,
        "stories":stories,
        "page_num": page,
        "total_pages": p.num_pages
      }, context_instance=RequestContext(request))
    
        
@login_required    
def story_queue( request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user )
    return render_to_response("extras/story_queue.html", {
        "project":project,
      }, context_instance=RequestContext(request))

@login_required
def syncronize_extra(request, project_slug, extra_slug):
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user )
    manager.syncronizeExtra( extra_slug, project )
    return HttpResponse("OK")

@login_required
def enable_extra( request, project_slug, extra_slug):
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user )
    manager.enableExtra(project,extra_slug)
    return HttpResponseRedirect(reverse("configure_extra_url",kwargs={'project_slug':project_slug, "extra_slug":extra_slug}))

@login_required
def disable_extra( request, project_slug, extra_slug):
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user )
    manager.disableExtra(project,extra_slug)
    return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project_slug}))

@login_required
def configure_extra( request, project_slug, extra_slug, stage=""):
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user )
    extra = manager.getExtra( extra_slug )
    if extra != None:
        return extra.doProjectConfiguration(request, project, stage)
    return HttpResponseRedirect(reverse("project_extras_url",kwargs={'project_slug':project_slug}))

@login_required
def project_extras(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    admin_access_or_403(project, request.user )
    return render_to_response("extras/project_extras.html", {
        "project":project,
        "extras":manager.getExtraConfigs(project)
      }, context_instance=RequestContext(request))

def project_extra_options( request, extra_slug, project_slug):
    pass
