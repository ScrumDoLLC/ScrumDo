import httplib, urllib
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from projects.access import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from projects.story_views import handleAddStory

@login_required
def play(request, project_slug ):
  project = get_object_or_404( Project, slug=project_slug )
  write_access_or_403(project, request.user )
  
  add_story_form = handleAddStory(request, project)
  return render_to_response("poker/play_poker.html",  {"project":project, "add_story_form":add_story_form } ,context_instance=RequestContext(request) )
  
@login_required
def control(request, project_slug ):
  pass
  