from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers

from xlrd import open_workbook

from django.conf import settings

import re

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from projects.models import Project, ProjectMember, Iteration, Story
from projects.forms import *



@login_required
def set_story_status( request, group_slug, story_id, status):
  story = get_object_or_404( Story, id=story_id )
  story.status = status;
  story.save();
  if( request.POST.get("return_type","mini") == "mini"):
    return render_to_response("stories/single_mini_story.html", {
        "story": story,
      }, context_instance=RequestContext(request))
  return render_to_response("stories/single_block_story.html", {
      "story": story,
    }, context_instance=RequestContext(request))


  
@login_required
def delete_story( request, group_slug, story_id ):
  if request.method == "POST":
    story = get_object_or_404( Story, id=story_id )  
    story.delete()     
    redirTo = request.GET.get("redirectTo", "")
    if redirTo:
      return HttpResponseRedirect(redirTo );
    else:
      return HttpResponse("OK");
  else:
    return HttpResponse("FAIL");
     
# This is the request handler that gets called from the story_list page when the user drags & drops a story to a
# new ranking or a new iteration.  It should have two post variables, index and iteration
@login_required
def reorder_story( request, group_slug, story_id):
  story = get_object_or_404( Story, id=story_id )
  project = get_object_or_404( Project, slug=group_slug )
  if request.method == 'POST':
    rank = 0
    target_rank = int(request.POST["index"])
    target_iteration = request.POST["iteration"]
    iteration = get_object_or_404( Iteration, id=target_iteration )
    story.rank = target_rank;
    story.iteration = iteration;
    story.save()
    
    stories = project.stories.all().filter(iteration=iteration).order_by("rank")
    
    # For now, a stupid reorder everything algorithm
    for otherStory in stories:
      if rank == target_rank:
        rank+=1
        
      if otherStory != story:        
        otherStory.rank = rank
        otherStory.save()      
        rank = rank + 1
        
    return HttpResponse("OK")
  return  HttpResponse("Fail")
  

@login_required
def mini_story( request, group_slug, story_id):
  story = get_object_or_404( Story, id=story_id )
  return render_to_response("stories/single_mini_story.html", {
      "story": story,
    }, context_instance=RequestContext(request))


def calculate_rank( project, general_rank ):
  if( general_rank == 0):
    return 0
  if( general_rank == 1):
    return round( project.stories.all().count() / 2)
  return project.stories.all().count()+1




@login_required
def story( request, group_slug, story_id ):
  story = get_object_or_404( Story, id=story_id )
  project = get_object_or_404( Project, slug=group_slug )
  return_type = request.GET.get("return_type","mini")

  if request.method == 'POST': # If the form has been submitted...
    form = StoryForm( project, request.POST, project, instance=story) # A form bound to the POST data    

    if form.is_valid(): # All validation rules pass      
      story = form.save(  )      

    if( request.POST['return_type'] == 'mini'):
      return render_to_response("stories/single_mini_story.html", {
          "story": story,         
        }, context_instance=RequestContext(request))
    if( request.POST['return_type'] == 'block'):
      return render_to_response("stories/single_block_story.html", {
          "story": story,         
        }, context_instance=RequestContext(request))
  
  else:
    form = StoryForm(project, instance=story )
  
  return   render_to_response("stories/story.html", {
      "story": story,
      "form": form,
      "project": project,
      "return_type": return_type
    }, context_instance=RequestContext(request))

@login_required
def stories_iteration(request, group_slug, iteration_id):
  project = get_object_or_404(Project, slug=group_slug)  
  iteration = get_object_or_404(Iteration, id=iteration_id, project=project)  
  
  order_by = request.GET.get("order_by","rank");
  display_type = request.GET.get("display_type","mini")
  text_search = request.GET.get("search","")
  tags_search = request.GET.get("tags","")

  tags_list = re.split('[, ]+', tags_search)

  # There's probably a better way to set up these filters...
  if text_search and tags_search:
    stories = iteration.stories.filter(story_tags__tag__name__in=tags_list).extra( where = ["MATCH(summary, detail, extra_1, extra_2, extra_3) AGAINST (%s IN BOOLEAN MODE)"], params=[text_search]).distinct()
  elif tags_search:
    stories = iteration.stories.filter(story_tags__tag__name__in=tags_list).distinct().order_by(order_by)
  elif text_search:
    stories = iteration.stories.extra( where = ["MATCH(summary, detail, extra_1, extra_2, extra_3) AGAINST (%s IN BOOLEAN MODE)"], params=[text_search]).order_by(order_by)
  else:
    stories = iteration.stories.order_by(order_by)

  return render_to_response("stories/mini_story_list.html", {
    "stories": stories,
    "project":project,
    "display_type": display_type
  }, context_instance=RequestContext(request))


@login_required
def stories(request, group_slug):
  project = get_object_or_404(Project, slug=group_slug)  

  if request.method == 'POST': # If the form has been submitted...
    form = StoryForm(project, request.POST) # A form bound to the POST data
    if form.is_valid(): # All validation rules pass
      story = form.save( commit=False )
      story.local_id = project.stories.all().count() + 1
      story.project = project
      story.creator = request.user
      story.iteration = project.get_default_iteration()
      story.rank = calculate_rank( project, int(form.cleaned_data['general_rank']) )
      story.save()
      request.user.message_set.create(message="New story created.")
      form = StoryForm(project)
  else:
    form = StoryForm(project)

  return render_to_response("stories/story_list.html", {
    "add_story_form": form,
    "project": project,
    "default_iteration_id": int(request.GET.get("iteration","-1"))

  }, context_instance=RequestContext(request))



@login_required
def import_file(request, group_slug):
  project = get_object_or_404(Project, slug=group_slug)
  
  if request.method == 'POST':     
      processImport(project, request.FILES['import_file'], request.user);
      return HttpResponseRedirect(reverse('project_detail', kwargs={'group_slug':project.slug}) )
  else:
      form = ImportForm()
      
  return render_to_response("projects/import.html", {
           "form":form,
        }, context_instance=RequestContext(request))
