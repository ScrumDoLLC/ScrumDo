import httplib, urllib
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from projects.access import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from projects.story_views import handleAddStory

from django.conf import settings
import json
import pprint
import logging
logger = logging.getLogger(__name__)

from projects.models import Story, Project
from projects.access import *

pp = pprint.PrettyPrinter(indent=4)

@login_required
def play(request, project_slug ):
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user )
    add_story_form = handleAddStory(request, project)
    hookbox_server = settings.HOOKBOX_HOST
    username = str( request.user )
    return render_to_response("poker/play_poker.html",  {"poker_channel_id":project.slug ,
                                                         "hookbox_server":hookbox_server, 
                                                         "project":project, 
                                                         "username":username,
                                                         "add_story_form":add_story_form } , context_instance=RequestContext(request) )



@login_required
def ajax(request, project_slug):
    action = request.POST.get("action")
    if action == "stories_to_size":
        return stories_to_size( request, project_slug )
    elif action == "stories_with_size":
        return stories_with_size( request, project_slug )
    elif action == "set_size":
        return set_story_size( request, project_slug )
    elif action == "single_story":
        return single_story(request, project_slug)
    elif action == "all_incomplete_stories_to_size":
        return all_stories(request, project_slug, True)
    elif action == "all_stories_to_size":
        return all_stories(request, project_slug, False)
    

def set_story_size( request, project_slug ):
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user )
    story = get_object_or_404( Story, id=request.POST.get("story") ) 
    if story.project != project :
        raise PermissionDenied()   # Shenanigans!
    story.points = request.POST.get("points")
    story.save()
    return HttpResponse("ok")
    
def single_story( request, project_slug ):
    project = get_object_or_404( Project, slug=project_slug )
    read_access_or_403(project, request.user )
    story = get_object_or_404( Story, id=request.POST.get("story") )
    if story.project != project :
        raise PermissionDenied()   # Shenanigans!
    
    return render_to_response("poker/single_story.html",  { "story":story } , context_instance=RequestContext(request) )
    

def stories_with_size( request, project_slug ):
    project = get_object_or_404( Project, slug=project_slug )
    read_access_or_403(project, request.user )
    stories = project.stories.filter(points=request.POST.get("size"))[:10];
    return render_to_response("poker/stories_with_size.html",  { "stories":stories } , context_instance=RequestContext(request) )
    
def all_stories(request, project_slug, only_incomplete):
    project = get_object_or_404( Project, slug=project_slug )
    read_access_or_403(project, request.user )
    
    if only_incomplete:
        stories = project.stories.exclude(status=Story.STATUS_DONE ).order_by("local_id");
    else:
        stories = project.stories.order_by("local_id");
        
    return render_to_response("poker/stories_to_size.html",  { "stories":stories } , context_instance=RequestContext(request) )    

def stories_to_size( request, project_slug ):
    project = get_object_or_404( Project, slug=project_slug )
    read_access_or_403(project, request.user )
    stories = project.stories.filter(points="?").order_by("rank");
    return render_to_response("poker/stories_to_size.html",  { "stories":stories } , context_instance=RequestContext(request) )

def hookbox_test(request):
    # For this to work you need hookbox installed and running with a command similar to:
    # hookbox -s juy789 --cbhost=localhost --cbport=8000 --cbpath=/poker/hookbox_callback -p 8080
    # for the scrumdo.com live site: hookbox -s OURSECRETKEY --cbhost=www.scrumdo.com --cbport=80 --cbpath=/poker/hookbox_callback -p 8080
    # Make sure your secret key in settings matches this one.

    hookbox_server = settings.HOOKBOX_HOST
    return render_to_response("poker/hookbox_test.html",  {"poker_session_id":"test-poker","hookbox_server":hookbox_server } ,context_instance=RequestContext(request) )

@login_required
def hookbox_callback_connect( request ):
    logger.debug("Hookbox connect callback ")
    pp.pprint(request.POST)
    if request.POST.get("secret") != settings.HOOKBOX_SECRET:
        raise PermissionDenied()

    # Occurs when someone joins, you should handle authorization here.
    return HttpResponse( json.dumps([ True, { "name" : str(request.user) } ]) )

@login_required
def hookbox_callback_create_channel(request):
    logger.debug("Hookbox create channel callback %s" % request.POST.get("channel_name"))
    pp.pprint(request.POST)
    if request.POST.get("secret") != settings.HOOKBOX_SECRET:
        raise PermissionDenied()
    # here is where you can handle the first person joining a planning poker session
    return HttpResponse(json.dumps([ True, { "history_size" : 0,
                                             "reflective" : True,                                             
                                             "presenceful" : True } ]) )

@login_required
def hookbox_callback_subscribe (request):
    logger.debug("Hookbox subscribe callback")
    pp.pprint(request.POST)
    if request.POST.get("secret") != settings.HOOKBOX_SECRET:
        raise PermissionDenied()
    
    project_slug = request.POST.get("channel_name")
    project = get_object_or_404(Project, slug=project_slug)
    read_access_or_403(project, request.user )  # make sure this user has access to this project
    
    return HttpResponse(json.dumps([ True, {} ]) )

@login_required
def hookbox_callback_unsubscribe (request):
    logger.debug("Hookbox unsubscribe callback")
    pp.pprint(request.POST)
    if request.POST.get("secret") != settings.HOOKBOX_SECRET:
        raise PermissionDenied()
    # Occurs when someone leaves - not sure how reliable this is.
    return HttpResponse(json.dumps([ True, {} ]) )

@login_required
def hookbox_callback_publish (request):
    logger.debug("Hookbox publish callback")
    pp.pprint(request.POST)
    if request.POST.get("secret") != settings.HOOKBOX_SECRET:
        raise PermissionDenied()
    # Called when a client calls the .publish method
    # This is where we should handle user input
    return HttpResponse(json.dumps([ True, {} ])  )

@login_required
def hookbox_callback_disconnect( request ):
    return HttpResponse(json.dumps([ True, {} ])  )
    
@login_required
def hookbox_callback_destroy_channel(request):
    return HttpResponse(json.dumps([ True, {} ])  )
