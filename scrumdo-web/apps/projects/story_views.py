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
import sys
import urllib
import re
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from haystack.query import SearchQuerySet
from xlrd import open_workbook

from projects.models import Project, ProjectMember, Iteration, Story, STATUS_REVERSE, Epic
from projects.forms import *
from projects.access import *
from projects.calculation import onDemandCalculateVelocity
import activities.utils as utils
import projects.signals as signals


logger = logging.getLogger(__name__)


@login_required
def story_permalink(request, story_id):
    "A permalink for a story.  No matter where it goes this should work"
    story = get_object_or_404( Story, id=story_id )
    read_access_or_403(story.project,request.user)
    return HttpResponseRedirect( "%s#story_%d" % (reverse("iteration", kwargs={'group_slug':story.project.slug,'iteration_id':story.iteration.id}),story.id) )
        
# View called via ajax on the iteration or iteration planning pages.  Meant to set the status of
# a story, and then return an html snippet that can be replaced on the page with the new status
@login_required
def set_story_status( request, group_slug, story_id, status):
    story = get_object_or_404( Story, id=story_id )
    write_access_or_403(story.project,request.user)
    if story.status != status:
        # the status was actually changes
        story.status = status;
        story.save();
        signals.story_status_changed.send( sender=request, story=story, user=request.user )
        # statuses = [None, "TODO", "In Progress", "Reviewing", "Done"]
        # story.activity_signal.send(sender=story, user=request.user, story=story, action="changed status", status=statuses[status], project=story.project)
        onDemandCalculateVelocity( story.project )

    organization = _organizationOrNone( story.project )

    if( request.POST.get("return_type","mini") == "mini"):
        return render_to_response("stories/single_mini_story.html", {
            "story": story,
            "return_type": "mini",
            "project": story.project,
            "organization": organization
          }, context_instance=RequestContext(request))
    if( request.POST.get("return_type","mini") == "queue"):
        return render_to_response("stories/single_queue_story.html", {
            "story": story,
            "return_type": "queue",
            "project": story.project,
            "organization": organization
      }, context_instance=RequestContext(request))
    return render_to_response("stories/single_block_story.html", {
            "story": story,
            "return_type": "block",
            "project": story.project,
            "organization": organization
      }, context_instance=RequestContext(request))



@login_required
def story_comments( request, story_id ):
    logger.debug("Retrieving comments for story")
    story = get_object_or_404( Story, id=story_id )
    read_access_or_403( story.project, request.user )
    return render_to_response("stories/story_comments.html", {
        "story": story,
      }, context_instance=RequestContext(request))

# Deletes a story.  No further confirmation, don't post here if you want your story.
# We're doing some confirmation client-side.  Sometimes called via ajax, sometimes
# a normal request.  If a normal request, there should be a GET param specifying where
# to send us to next.
@login_required
def delete_story( request, group_slug, story_id ):
    logger.debug("Deleting story %s" % str(story_id))
    if request.method == "POST":
        story = get_object_or_404( Story, id=story_id )
        write_access_or_403(story.project,request.user)
        signals.story_deleted.send( sender=request, story=story, user=request.user )
        # story.activity_signal.send(sender=story, user=request.user, story=story, action="deleted", project=story.project)
        story.sync_queue.clear()
        story.delete()
        onDemandCalculateVelocity( story.project )

        redirTo = request.GET.get("redirectTo", "")
        if redirTo:
            return HttpResponseRedirect(redirTo);
        else:
            return HttpResponse("OK");
    else:
        return HttpResponse("FAIL");

# Request handler for the scrum board ajax calls
@login_required
def scrum_board( request, group_slug, story_id):
    status_map = {"todo":Story.STATUS_TODO, "doing":Story.STATUS_DOING, "reviewing":Story.STATUS_REVIEWING, "done":Story.STATUS_DONE};
    story = get_object_or_404( Story, id=story_id )
    project = get_object_or_404( Project, slug=group_slug )
    if request.method == 'POST':
        if request.POST.get("status",None) == None:
            return HttpResponse("FAILED")
        target_status = status_map[request.POST.get("status")]
        reorderStory( story, request.POST.get("before"), request.POST.get("after"), story.iteration, field_name="board_rank")
        if story.status != target_status:
            story.status = target_status
            story.save()            
            signals.story_status_changed.send( sender=request, story=story, user=request.user)            
            onDemandCalculateVelocity( story.project )
        else:
            story.save()
    return HttpResponse("OK")



@login_required
def reorder_epic( request, group_slug, epic_id):
    epic = get_object_or_404( Epic, id=epic_id )
    project = get_object_or_404( Project, slug=group_slug )
    if epic.project != project:
        raise PermissionDenied()
    write_access_or_403(project,request.user)
    if request.method == 'POST':
        rank = 0
        target_iteration = request.POST["iteration"]

        try:
            iteration = get_object_or_404( Iteration, id=target_iteration )
        except:
            iteration = story.iteration

        if request.POST.get("action","") == "reorder" :
            reorderEpic( epic, request.POST.get("before"), request.POST.get("after"), iteration)            

        epic.iteration = iteration
        epic.save()
        
        return HttpResponse("OK")
    return  HttpResponse("Fail")


def _deleteEpic( epic ):
    for story in epic.stories.all():
        story.epic = None
        story.save()
    for epic in epic.children.all():
        epic.parent = None
        epic.save()
    epic.delete()    
    

@login_required
def delete_epic(request,  epic_id):
    epic = get_object_or_404(Epic, id=epic_id)
    project = epic.project
    write_access_or_403(project, request.user)
    if request.method == 'POST': # If the form has been submitted...        
        _deleteEpic( epic )
        return HttpResponse("OK")
    

@login_required
def edit_epic(request,  epic_id):
    epic = get_object_or_404(Epic, id=epic_id)
    project = epic.project
    write_access_or_403(project, request.user)
    
    if request.method == 'POST': # If the form has been submitted...        
        form = EpicForm( project, request.POST, instance=epic)
        if form.is_valid(): # All validation rules pass
            epic = form.save()
            onDemandCalculateVelocity(project)
            return HttpResponse("OK")
    else:
        form = EpicForm( project,  instance=epic)
    
    return render_to_response("projects/epic_edit.html", {
        "form":form,
        "epic":epic,
        "project":project
      }, context_instance=RequestContext(request))

# This is the request handler that gets called from the story_list and iteraqtion pages when the user drags & drops a story to a
# new ranking or a new iteration.  It should have two post variables, index and iteration
@login_required
def reorder_story( request, group_slug, story_id):
    story = get_object_or_404( Story, id=story_id )
    project = get_object_or_404( Project, slug=group_slug )
    write_access_or_403(project,request.user)
    if request.method == 'POST':
        old_story = story.__dict__.copy()
        
        rank = 0
        target_iteration = request.POST.get("iteration","")

        try:
            iteration = get_object_or_404( Iteration, id=target_iteration )
        except:
            iteration = story.iteration

        if request.POST.get("action","") == "reorder" :
            old_story = story.__dict__.copy()
            reorderStory( story, request.POST.get("before"), request.POST.get("after"), iteration)            
            diffs = utils.model_differences(old_story, story.__dict__, dicts=True)
            signals.story_updated.send( sender=request, story=story, user=request.user, diffs=diffs )            
            # story.activity_signal.send(sender=story, user=request.user, story=story, action="reordered", project=project)

        if request.POST.get("epic","-1") != "-1":
            epic_id = request.POST.get("epic")
            epic = Epic.objects.get(id=epic_id)
            if epic and epic.project == project:
                story.epic = epic
        elif request.POST.get("epic","") == "-1":
            # Explicitly moving it out of any epic
            story.epic = None


        story.iteration = iteration
        story.save()
        diffs = utils.model_differences(old_story, story.__dict__, dicts=True)

        return HttpResponse("OK")
    return  HttpResponse("Fail")

def reorderEpic(epic, before_id, after_id, iteration, field_name="order"):
    "Reorders an epic between two others."
    epic_rank_before = 0
    epic_rank_after = 999999 # max value of the DB field

    # If there is a epic that should be before this one, grab it's rank
    try:
        epic_before = Epic.objects.get( id=before_id )
        epic_rank_before = epic_before.__dict__[field_name]
    except:
        pass

    # If  there is a epic that should be after this one, grab it's rank.
    try:
        epic_after = Epic.objects.get( id=after_id )
        epic_rank_after = epic_after.__dict__[field_name]
    except:
        pass

    diff = abs(epic_rank_after - epic_rank_before)
    try:
        if diff > 1:
            # It fits between them            
            epic.__dict__[field_name] = round(diff/2) + epic_rank_before
            logger.debug("Reordering epic fit %d %d %d" % (epic_rank_before, epic.__dict__[field_name], epic_rank_after) )
            return
    except:
        pass # do an emergency re-order below if things are falling out of bounds.

    # It doesn't fit!  reorder everything!
    epics = iteration.epics.all().order_by(field_name)

    rank = 10
    for other_epic in epics:
        if other_epic.__dict__[field_name] == epic_rank_after:
            # We should always have a epic_rank_after if we get here.
            epic.__dict__[field_name] = rank
            rank += 20
        other_epic.__dict__[field_name] = rank
        other_epic.save()
        rank += 20




def reorderStory( story, before_id, after_id, iteration, field_name="rank"):
    "Reorders a story between two others."
    story_rank_before = 0
    story_rank_after = 999999 # max value of the DB field

    # If there is a story that should be before this one, grab it's rank
    try:
        story_before = Story.objects.get( id=before_id )
        story_rank_before = story_before.__dict__[field_name]
    except:
        pass

    # If  there is a story that should be after this one, grab it's rank.
    try:
        story_after = Story.objects.get( id=after_id )
        story_rank_after = story_after.__dict__[field_name]
    except:
        pass

    diff = abs(story_rank_after - story_rank_before)
    # logger.debug("Before %d , after %d, diff %d" % (story_rank_after, story_rank_before, diff) )
    try:
        if diff > 1:
            # It fits between them
            # logger.debug(round(diff/2) )
            story.__dict__[field_name] = round(diff/2) + story_rank_before
            logger.debug("Reordering fit %d %d %d" % (story_rank_before, story.__dict__[field_name], story_rank_after) )
            return
    except:
        pass # do an emergency re-order below if things are falling out of bounds.

    # It doesn't fit!  reorder everything!
    stories = iteration.stories.all().order_by(field_name)

    rank = 10
    for other_story in stories:
        if other_story.__dict__[field_name] == story_rank_after:
            # We should always have a story_rank_after if we get here.
            story.__dict__[field_name] = rank
            rank += 20
        other_story.__dict__[field_name] = rank
        other_story.save()
        rank += 20





# On the iteration planning page, this renders one story view.  Generally called
# via ajax.
@login_required
def mini_story( request, group_slug, story_id):
    story = get_object_or_404( Story, id=story_id )
    read_access_or_403(story.project,request.user)
    return render_to_response("stories/single_mini_story.html", {
        "story": story,
      }, context_instance=RequestContext(request))


def _calculate_rank( iteration, general_rank ):
    """ calculates the rank a new story should have for a project based off of 3 general rankings.
    0=top, 1=middle, 2=bottom
    TODO (Improvement) - I'd like to re-think how ranking is done for both initial and adjustments of ranks.
    """
    try:
        stories = iteration.stories.all().order_by("rank")
        story_count = len(stories)
        print "%d %s" % (story_count, [story.rank for story in stories])
        if story_count == 0:
            return 10

        if( general_rank == 0): # top
            return int(stories[0].rank / 2)

        if( general_rank == 1): # middle
            if story_count < 2:
                return 10
            s1_rank = stories[ int(story_count/2) - 1 ].rank
            s2_rank = stories[ int(story_count/2) ].rank
            return int( (s1_rank + s2_rank) / 2 )

        return stories[ story_count - 1 ].rank + 10
    except:
        return 10

@login_required
def story_block(request, story_id):
    story = get_object_or_404( Story, id=story_id )
    read_access_or_403( story.project, request.user )
    organization = _organizationOrNone( story.project )
    template = "stories/single_block_story.html"
    if request.GET.get("story_type") == "scrumboard":
        template = "stories/single_scrum_board_story.html"
    return render_to_response(template, {
        "story": story,
        "return_type": "block",
        "project": story.project,
        "organization": organization
      }, context_instance=RequestContext(request))

# Returns the edit-story form, with minimal html wrapper.  This is useful for displaying within
# a facebox popup.
# One place it's used is on the iteration page when you click the magnifying glass for a story.
@login_required
def story_edit(request, group_slug, story_id):
    story = get_object_or_404( Story, id=story_id )
    project = get_object_or_404( Project, slug=group_slug )
    return_type = request.GET.get("return_type","mini")

    if request.method == 'POST': # If the form has been submitted...
        old_story = story.__dict__.copy()
        write_access_or_403(project,request.user)
        form = StoryForm( project, request.POST, project, instance=story) # A form bound to the POST data

        if form.is_valid(): # All validation rules pass
            story = form.save(commit=False)
            

            if request.POST.get("category_name","") != "":
                try:
                    category_name = request.POST.get("category_name")
                    category_name = category_name.replace(",","").strip()
                    category_name = category_name[:50]
                    if not category_name in project.getCategoryList():
                        project.categories = "%s, %s" % (project.categories, category_name)
                        if len(project.categories) <= 1024:
                            project.save()
                        else:
                            request.user.message_set.create(message="Too many categories")
                    story.category = category_name
                except:
                    pass # no category to use
                
            story.save()
            
            diffs = utils.model_differences(old_story, story.__dict__, dicts=True)
            activities = 0

            signals.story_updated.send( sender=request, story=story, diffs=diffs, user=request.user )
            onDemandCalculateVelocity( project )

        organization = _organizationOrNone( project )
        if( request.POST['return_type'] == 'mini'):
            return render_to_response("stories/single_mini_story.html", {
                "story": story,
                "return_type": return_type,
              }, context_instance=RequestContext(request))
        if( request.POST['return_type'] == 'scrumboard'):
            return render_to_response("stories/single_scrum_board_story.html", {
                "story": story,
                "return_type": return_type,
                "project": story.project,
                "organization": organization
              }, context_instance=RequestContext(request))
        if( request.POST['return_type'] == 'block'):
            return render_to_response("stories/single_block_story.html", {
                "story": story,
                "return_type": return_type,
                "project": story.project,
                "organization": organization
              }, context_instance=RequestContext(request))
        if( request.POST['return_type'] == 'queue'):
            return render_to_response("stories/single_queue_story.html", {
                "story": story,
                'project': story.project,
                "organization": organization,
                "return_type": return_type,
              }, context_instance=RequestContext(request))

    else:
        read_access_or_403(project,request.user)
        form = StoryForm(project, instance=story )

    tags = project.unique_tags()

    return   render_to_response("stories/story.html", {
        "story": story,
        "form": form,
        "project": project,
        "return_type": return_type
      }, context_instance=RequestContext(request))

@login_required
def stories_scrum_board(request, group_slug, iteration_id, status):
    project = get_object_or_404(Project, slug=group_slug)
    read_access_or_403(project,request.user)
    iteration = get_object_or_404(Iteration, id=iteration_id, project=project)


    stories = iteration.stories.select_related('project', 'project__organization','project__organization__subscription',  'iteration','iteration__project',).filter(status=STATUS_REVERSE[status]).order_by("board_rank")

    return render_to_response("stories/scrum_board_story_list.html", {
    "stories": stories,
    "project":project
    }, context_instance=RequestContext(request))


@login_required
def epic(request, epic_id):
    "Returns a snippet of html suitable for use in replacing an epic block on the backlog pages."
    epic = get_object_or_404(Epic, id=epic_id)
    project = epic.project
    read_access_or_403(project,request.user)
    organization = _organizationOrNone( project )
    return render_to_response("projects/epic.html", {
    "epic": epic,
    "organization":organization,
    "project":project
    }, context_instance=RequestContext(request))

# Returns the stories for a given iteration as an html snippet.  The iteration planning page uses this
# uplon load, and then also upon filtering by the user
@login_required
def stories_iteration(request, group_slug, iteration_id, page=1):
    page = int(page)
    project = get_object_or_404(Project, slug=group_slug)
    read_access_or_403(project,request.user)
    iteration = get_object_or_404(Iteration, id=iteration_id, project=project)

    order_by = request.GET.get("order_by","rank")
    display_type = request.GET.get("display_type","mini")
    text_search = request.GET.get("search","").strip()
    tags_search = request.GET.get("tags","").strip()
    category = request.GET.get("category","").strip()
    clrbtn = request.GET.get("clearButton",'')
    only_assigned = request.GET.get("only_assigned", False)
    backlog_mode = request.GET.get("backlog_mode", False)
    paged = "True" == request.GET.get("paged", "True")

    if request.GET.get("clearButton") == "Clear Filter":
        text_search = ""
        tags_search = ""
        category =""

    if only_assigned == "False":
        only_assigned = False

    # Store the query string, so it can be passed back for subsequent page requests.
    query_string = urllib.urlencode( {   'order_by':order_by,
                                         'display_type':display_type,
                                         'search':text_search.encode('utf-8'),
                                         'tags':tags_search.encode('utf-8'),
                                         'category':category.encode('utf-8'),
                                         'only_assigned':only_assigned,
                                         'clearButton':clrbtn
                                         })
    has_next = False
    if text_search == "":
        # Don't need to consult our solr search engine.
        has_next, stories = _getStoriesNoTextSearch( iteration, order_by, tags_search, category, only_assigned, request.user, paged, page, backlog_mode)
    else:
        # we need some fancy-schmancy searching
        stories = _getStoriesWithTextSearch( iteration, text_search, order_by, tags_search, category, only_assigned, request.user, backlog_mode)

    organization = _organizationOrNone( project )

    return render_to_response("stories/mini_story_list.html", {
      "stories": stories,
      "project":project,
      "return_type":display_type,
      "display_type": display_type,
      "load_next_page": has_next ,
      "next_page_num": page+1,
      "next_page_query_string":query_string,
      "iteration_id": iteration.id,
      "organization": organization
    }, context_instance=RequestContext(request))

def _organizationOrNone(project):
    try:
        organization = project.organization
    except Organization.DoesNotExist:
        organization = None
    return organization

def _getStoriesWithTextSearch( iteration, text_search, order_by, tags_search, category, only_assigned, user, backlog_mode):
    search_results = SearchQuerySet().filter(project_id=iteration.project.id).filter(iteration_id=iteration.id).filter(content=text_search).models(Story).order_by(order_by).load_all()
    if tags_search != "":
        search_results = search_results.filter(tags=tags_search)
    if category != "":
        search_results = search_results.filter(category=category)
    if only_assigned:
        search_results = search_results.filter(user_id=user.id)
    stories = [ result.object for result in search_results]
    return stories

def _getStoriesNoTextSearch( iteration, order_by, tags_search, category, only_assigned, user, paged, page, backlog_mode):
    tags_list = re.split('[, ]+', tags_search)

    stories = iteration.stories

    if order_by != "numeric_points":
        stories = stories.order_by(order_by)
    else:
        # Tried a few things here... CAST(points as SIGNED) in the order_by clause would have been preferred, but I couldn't get that through
        # the ORM.  Secondary, I tried craeting a custom column assigned to that, but it caused the query to fail.  The 0+string is a bit
        # of a mysql specific hack to convert a string to a number.
        stories = stories.extra(select={'numeric_points': '0+points'}).order_by(order_by)

    if tags_search:
        stories = stories.filter(story_tags__tag__name__in=tags_list).distinct().order_by(order_by)
    if only_assigned:
        stories = stories.filter(assignee=user)
    if category:
        stories = stories.filter(category=category)
    if backlog_mode:
        stories = stories.filter(epic=None)

    stories = stories.select_related('project', 'project__organization','project__organization__subscription', 'iteration',)

    if paged:
        paginator = Paginator(stories, 50)
        page_obj = paginator.page(page)
        has_next = page_obj.has_next()
        stories = page_obj.object_list
    else:
        has_next = False

    return (has_next, stories)

@login_required
def ajax_add_story( request, group_slug):
    project = get_object_or_404(Project, slug=group_slug)

    if request.method == "POST" and request.POST.get("action") == "addStory":
        form = AddStoryForm(project, request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            story = _handleAddStoryInternal( form , project, request)
            return render_to_response("stories/story_added.html", {"story": story}, context_instance=RequestContext(request))

    # A story wasn't created...
    return HttpResponse("")




def _handleAddStoryInternal( form , project, request):
    story = form.save( commit=False )
    story.local_id = project.getNextId()
    story.project = project
    story.creator = request.user
    iteration_id = request.POST.get("iteration",None)
    epic_id = request.POST.get("epic",None)

    if iteration_id != None:
        iteration = get_object_or_404(Iteration, id=iteration_id)
        if iteration.project != project:
            raise PermissionDenied() # Shenanigans!
        story.iteration = iteration
    else:
        story.iteration = project.get_default_iteration()

    if epic_id != None and epic_id != "":
        epic = Epic.objects.get(id=epic_id)
        if epic.project != project:
            raise PermissionDenied() # Shenanigans!
        story.epic = epic

    try:
        general_rank = int(form.cleaned_data['general_rank'])
    except:
        general_rank = 2 # bottom



    if request.POST.get("category_name") != "":
        category_name = request.POST.get("category_name","")
        category_name = category_name.replace(",","").strip()
        category_name = category_name[:50]
        if not category_name in project.getCategoryList():            
            project.categories = "%s, %s" % (project.categories, category_name)
            if len(project.categories) <= 1024:
                project.save()
            else:
                request.user.message_set.create(message="Too many categories")                        
        story.category = category_name
        

    story.rank = _calculate_rank( story.iteration, general_rank )
    # logger.info("New Story %s" % story.summary)
    story.save()
    if story.points_value() > 0:
        onDemandCalculateVelocity( project )
    signals.story_created.send( sender=request, story=story, user=request.user )
    # story.activity_signal.send(sender=story, user=request.user, story=story, action="created", project=project)
    request.user.message_set.create(message="Story #%d created." % story.local_id )
    return story


def handleAddStory( request , project ):
    """ Handles the add story form.
        Various views have an add story form on them.  This method handles that,
        and returns a new StoryForm object the view can use. """
    if request.method == "POST" and request.POST.get("action") == "addStory":
        form = AddStoryForm(project, request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            story = _handleAddStoryInternal( form , project, request)
        else:
            return form
    return AddStoryForm( project )


# The iteration planning tool.  It can also handle the add story form.
# TODO (cleanup): We should factor out the add story form functionality
# TODO (cleanup): We should rename this method, and likely rename the URL that points at it as well.
@login_required
def stories(request, group_slug):
    project = get_object_or_404(Project, slug=group_slug)
    write_access_or_403(project,request.user)

    form = handleAddStory(request, project )

    return render_to_response("stories/iteration_planning.html", {
      "add_story_form": form,
      "project": project,
      "return_type":"mini",
      "current_view":"iteration_planning",
      "default_iteration_id": int(request.GET.get("iteration","-1"))

    }, context_instance=RequestContext(request))



def pretty_print_story(request, group_slug, story_id):
    """Returns an html snippet that we use for a read-only full view of the story.  Right now, this is used
       when you mouse-hover over the eye icon for a story on an iteration page.  """
    story = get_object_or_404(Story, id=story_id)
    read_access_or_403( story.project, request.user )

    return render_to_response("stories/single_story_read_only.html", {
        "story": story
    }, context_instance=RequestContext(request))

def ajax_add_epic(request, group_slug):
    project = get_object_or_404(Project, slug=group_slug)
    write_access_or_403(project,request.user)
    if request.method == 'POST': # If the form has been submitted...        
        form = EpicForm( project, request.POST)
        if form.is_valid(): # All validation rules pass
            epic = form.save()
            onDemandCalculateVelocity(project)
            return HttpResponse(epic.id)
    return HttpResponse("")