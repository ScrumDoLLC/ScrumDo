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


from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers
import json
import datetime
import math
import logging

from projects.limits import org_project_limit, personal_project_limit

logger = logging.getLogger(__name__)


from xlrd import open_workbook

from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from projects.access import *
from projects.models import Project, ProjectMember, Iteration, Story
from projects.forms import *
from projects.import_export import exportProject
from organizations.models import Organization
from activities.models import Activity, StoryActivity, IterationActivity
import datetime

from story_views import handleAddStory

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM topics_topic
WHERE
    topics_topic.object_id = projects_project.id AND
    topics_topic.content_type_id = %s
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM projects_projectmember
WHERE projects_projectmember.project_id = projects_project.id
"""


# The homepage of the site...
# For logged in users, this includes the list of projects & organizations they are a member of.
def home( request ):
    my_projects = [];
    member_projects = [];
    organizations = [];
    activities=[]
    next_page = False

    if request.user.is_authenticated():
        organizations = Organization.getOrganizationsForUser(request.user)
        activities = Activity.getActivitiesForUser(request.user)

        assigned_stories = Story.getAssignedStories(request.user)

        paginator = Paginator(activities, 10)
        page_obj = paginator.page(1)
        activities = page_obj.object_list
        next_page = page_obj.has_next()

        memberships = ProjectMember.objects.filter( user=request.user )
        for membership in memberships:
            try:

                if( membership.project.creator_id == request.user.id):
                    my_projects.append(membership.project)
                else:
                    member_projects.append( membership.project )
            except:
                pass

        num_projects = len(member_projects) + len(filter(lambda p: p.organization == None, my_projects))
        blank_state = True if (num_projects + len(organizations)) == 0 else False
        return render_to_response("homepage.html", {
           "my_projects":my_projects,
           "my_organizations": organizations,
           "activities": activities,
           "activities_next_page":next_page,
           "assigned_stories": assigned_stories,
           "return_type" : "queue", # for the queue mini stories
           "member_projects":member_projects,
           "num_projects":num_projects,
           "now": datetime.datetime.now(),
           "blank_state" : blank_state
          }, context_instance=RequestContext(request))
    else:
        return render_to_response("unauthenticated_homepage.html", context_instance=RequestContext(request))

@login_required
def usage(request):
    organizations = Organization.getOrganizationsForUser( request.user )
    return render_to_response("usage_restrictions.html", {"organizations":organizations}, context_instance=RequestContext(request))


# The project admin page, this is where you can change the title, description, etc. of a project.
@login_required
def project_admin( request, group_slug ):
    project = get_object_or_404( Project, slug=group_slug )

    admin_access_or_403(project, request.user )

    form = ProjectOptionsForm(instance=project)

    if request.method == 'POST': # If one of the three forms on the page has been submitted...
        if request.POST.get("action") == "updateProject":
            form = ProjectOptionsForm( request.POST, instance=project)
            if form.is_valid(): # All validation rules pass
                story = form.save( commit=False )
                story.local_id = project.stories.count() + 1
                story.project = project
                story.creator = request.user
                story.save()
                request.user.message_set.create(message="Project options Saved.")
                return HttpResponseRedirect(reverse("project_detail",kwargs={'group_slug':project.slug}))
        if request.POST.get("action") == "moveToOrganization":
            organization = get_object_or_404( Organization, id=request.POST.get("organization_id",""))
            project.organization = organization
            project.save()
            request.user.message_set.create(message="Project added to organization")
            return HttpResponseRedirect(reverse("organization_detail",kwargs={'organization_slug':organization.slug}))
        if request.POST.get("action") == "removeFromOrganization":
            if request.POST.get("remove") == "on":
                for team in project.organization.teams.all():
                    if project in team.projects.all():
                        team.projects.remove(project)
                project.organization = None
                project.save()
                request.user.message_set.create(message="Project removed from organization")

    if project.organization:
        organizations = None
    else:
        organizations = Organization.getAdminOrganizationsForUser(request.user)

    return render_to_response("projects/project_admin.html", {
        "project": project,
        "form": form,
        "organizations": organizations
      }, context_instance=RequestContext(request))


# Returns a JSON feed for a given project/iteration that can be transformed with some javascript
# into a burn up chart.
@login_required
def iteration_burndown(request, group_slug, iteration_id):
    project = get_object_or_404( Project, slug=group_slug )
    read_access_or_403(project, request.user )
    iteration = get_object_or_404( Iteration, id=iteration_id )
    total_points = [];
    claimed_points = [];

    for log in iteration.points_log.all():
        total_points.append( [log.timestamp(), log.points_total] );
        claimed_points.append( [log.timestamp(), log.points_claimed] );

    total_stats = { "label":"Total Points", "data":_reduce_burndown_data(total_points)}
    claimed_stats = { "label":"Claimed Points", "data":_reduce_burndown_data(claimed_points)}

    json_serializer = serializers.get_serializer("json")()
    result = json.dumps([total_stats,claimed_stats])
    return HttpResponse(result) #, mimetype='application/json'


# Returns a JSON feed for a given project that can be transformed with some javascript
# into a burn up chart.
@login_required
def project_burndown(request, group_slug):
    project = get_object_or_404( Project, slug=group_slug )
    read_access_or_403(project, request.user )
    total_points = [];
    claimed_points = [];

    for log in project.points_log.all():
        total_points.append( [log.timestamp(), log.points_total] );
        claimed_points.append( [log.timestamp(), log.points_claimed] );

    total_stats = { "label":"Total Points", "data":_reduce_burndown_data(total_points)}
    claimed_stats = { "label":"Claimed Points", "data":_reduce_burndown_data(claimed_points)}


    json_serializer = serializers.get_serializer("json")()
    result = json.dumps([ total_stats , claimed_stats ])
    return HttpResponse(result) #, mimetype='application/json'

def _reduce_burndown_data( data ):
    """Takes a list of datapoints for a burnup chart and if there are more than 30, removes any redundant points.
       Redundant is when a point's two neighbors are equal to itself so it would just be a marker on a straight line.
       (I guess points along a straight sloped line could be considered redundant, but we don't remove those)
       The middle 15 is considered redundant here: [5,6,10,10,15,15,15,20]
       The middle 4 threes are considered redundant here: [1,2,3,3,3,3,3,3,5]
    """
    if len(data) < 30:
        return data
        
    subset = data[1:-1] # Subset of data that never includes first/last
    remove = []     
    for idx,item in enumerate( subset ):
                # idx = index before this item in data
                # idx+1 = this item in data
                # idx+2 = next item in data
        last_val = data[ idx ][1]
        next_val = data[ idx+2 ][1]

        if item[1]==last_val and item[1]==next_val:
            # don't need this item!
            remove.append(idx+1)
            # logger.debug("Can remove %d" % (idx+1))
    
    remove.reverse()
    for remove_index in remove:
        del data[remove_index:(remove_index+1)]
    return data


# The project history page, which lets you see a burn up chart for each past iteration.
@login_required
def project_history( request, group_slug ):
    project = get_object_or_404( Project, slug=group_slug )
    read_access_or_403(project, request.user )

    return render_to_response("projects/project_history.html", {
        "project": project,
      }, context_instance=RequestContext(request))

# Form and handler for creating a new project.
@login_required
def create(request, form_class=ProjectForm, template_name="projects/create.html"):
    project_form = form_class(request.POST or None)
    admin_organizations = Organization.getOrganizationsForUser( request.user ) # The user can create projects in organizations the user is an admin in.

    if project_form.is_valid():
        project = project_form.save(commit=False)
        project.creator = request.user
        org_id = request.POST.get("organization","none")
        organization = None
        if org_id != "none":
            organization = Organization.objects.filter( id=org_id )[0]

        creationAllowed = True

        if organization:
            creationAllowed = org_project_limit.increaseAllowed(organization=organization)
        else:
            creationAllowed = personal_project_limit.increaseAllowed(user=request.user)

        if creationAllowed:

            project.save()

            if organization != None:
                if organization in admin_organizations: # make sure the specified organization is in the list of admin orgs, if not silently ignore it.
                    addProjectToOrganization(project, organization)

            # We better make the user a member of their own project.
            project_member = ProjectMember(project=project, user=request.user)
            project.members.add(project_member)
            project_member.save()

            # And lets make the default backlog iteration with no start/end dates.
            default_iteration = Iteration( name='Backlog', detail='', default_iteration=True, project=project)
            project.iterations.add(default_iteration)
            default_iteration.save()

            request.user.message_set.create(message="Project Created")
            # Finished successfully creating a project, send the user to that page.
            return HttpResponseRedirect(project.get_absolute_url())
        else:
            return HttpResponseRedirect( reverse("usage") )

    # If they got here from the organziation page, there will be an org get-param set stating what organization it was from.
    # we need that here so it's pre-selected in the form.
    organization = None
    if request.GET.get("org","") != "":
        organization = Organization.objects.filter(id=request.GET.get("org",""))[0]

    return render_to_response(template_name, {
        "project_form": project_form,
        "admin_organizations":admin_organizations,
        "organization":organization
    }, context_instance=RequestContext(request))


def addProjectToOrganization( project, organization):
    logger.info("Adding project %s to organization %s" % (project.slug, organization.slug))
    project.organization = organization
    project.save()
    admin_teams = organization.teams.filter(access_type="admin")
    admin_team = admin_teams[0]
    if not admin_team:
    # This really shouldn't happen, there's no way to delete that default admin team.
        logger.error('Organization %s has no admin team' % organization.slug )
        return
    admin_team.projects.add( project )
    admin_team.save()



# A debug view to generate test data.
@login_required
def test_data(request, group_slug, count):
    project = get_object_or_404(Project, slug=group_slug)
    admin_access_or_403(project, request.user )
    count = int(count)
    story_count = project.stories.all().count()
    for i in range(count) :
        story = Story( rank=i + story_count,
                       summary="Test story #" + str(story_count+i),
                       local_id=i + story_count,
                       detail="Test story detail data",
                       creator=request.user,
                       points=5,
                       iteration=project.get_default_iteration(),
                       project=project);
        story.save();
    return HttpResponse("OK")

# Got rid of this view, just show your_projects now
@login_required
def projects(request, template_name="projects/projects.html"):
    return your_projects(request, template_name)

# A debug/tech-support view that re-numbers all of the stories for a project.
@login_required
def fix_local_id(request, group_slug=None):
    project = get_object_or_404(Project, slug=group_slug)
    admin_access_or_403(project, request.user )
    id = 1
    for story in project.stories.all().order_by("local_id"):
        story.local_id = id
        story.save()
        id = id + 1
    return HttpResponse("OK")

@login_required
def delete(request, group_slug=None, redirect_url=None):
    project = get_object_or_404(Project, slug=group_slug)
    admin_access_or_403(project, request.user )
    if not redirect_url:
        redirect_url = reverse('home')


    project.delete()
    request.user.message_set.create(message=_("Project %(project_name)s deleted.") % {"project_name": project.name})

    return HttpResponseRedirect(redirect_url)


@login_required
def your_projects(request, template_name="projects/your_projects.html"):
    projects = Project.objects.filter(member_users=request.user).order_by("name")
    content_type = ContentType.objects.get_for_model(Project)

    projects = projects.extra(select=SortedDict([
        ('member_count', MEMBER_COUNT_SQL),
        ('topic_count', TOPIC_COUNT_SQL),
        ]), select_params=(content_type.id,))

    return render_to_response(template_name, {
        "projects": projects,
    }, context_instance=RequestContext(request))




@login_required
def project(request, group_slug=None, form_class=ProjectUpdateForm, adduser_form_class=AddUserForm,
        template_name="projects/project.html"):
    project = get_object_or_404(Project, slug=group_slug)
    read_access_or_403(project, request.user )
    if not request.user.is_authenticated():
        is_member = False
    else:
        is_member = project.user_is_member(request.user)

    action = request.POST.get("action")
    if action == "update":
        write_access_or_403(project, request.user )
        project_form = form_class(request.POST, instance=project)
        if project_form.is_valid():
            project = project_form.save()
    else:
        project_form = form_class(instance=project)
    if action == "add":
        write_access_or_403(project, request.user )
        adduser_form = adduser_form_class(request.POST, project=project, user=request.user)
        if adduser_form.is_valid():
            adduser_form.save(request.user)
            adduser_form = adduser_form_class(project=project, user=request.user) # clear form
    else:
        adduser_form = adduser_form_class(project=project, user=request.user)

    add_story_form = handleAddStory(request, project)

    return render_to_response(template_name, {
        "project_form": project_form,
        "adduser_form": adduser_form,
        "add_story_form": add_story_form,
        "project": project,
        "group": project, # @@@ this should be the only context var for the project
        "is_member": is_member,
        "current_view":"project_page"
    }, context_instance=RequestContext(request))


# Drives the prediction page
# example: /projects/project/sch-r180-dashboards/project_prediction
@login_required
def project_prediction(request, group_slug):
    project = get_object_or_404(Project, slug=group_slug)
    read_access_or_403(project, request.user )
    stories = project.get_default_iteration().stories.exclude(status=Story.STATUS_DONE).order_by("rank")

    # there is a form on the page with velocity, iteration length, and carry over.
    # IF they're filled out, we should override the default values.
    requested_velocity = request.GET.get("velocity","x");
    if requested_velocity.isdigit():
        velocity = int( requested_velocity )
    else:
        velocity = project.velocity
    if velocity == 0 or velocity == None:
        # A default velocity just in case this project doesn't have one yet.
        velocity = 25
    requested_length = request.GET.get("iteration_length","x")
    if requested_length.isdigit():
        iteration_length = int( requested_length )
    else:
        iteration_length = 14
    carry_over = (request.GET.get("carry_over","x") == "on")


    points_left = velocity
    temp_stories = []
    predictions = []
    iteration_number = project.iterations.count()
    start_date = datetime.date.today()
    current_iterations = project.get_current_iterations()
    unsized_stories = []
    total_points = 0

    # Find when the last scheduled iteration ends.
    for iteration in current_iterations:
        if iteration.end_date > start_date:
            start_date = iteration.end_date



    # loop through the stories, and try to put them into a predicted iteration.
    for story in stories:
        if story.points_value() > points_left:
            record_prediction(predictions,temp_stories,iteration_number,start_date,iteration_length,points_left)
            iteration_number += 1
            if carry_over:
                points_left += velocity
            else:
                points_left = velocity
            temp_stories = []
            start_date += datetime.timedelta(days=iteration_length)
        if not story.points.isdigit():
            unsized_stories.append(story)
        points_left -= int(story.points_value())
        total_points += story.points_value()
        temp_stories.append(story)

    record_prediction(predictions,temp_stories,iteration_number,start_date,iteration_length,points_left)

    return render_to_response("projects/project_prediction.html", {
        "project": project,
        "predictions": predictions,
        "velocity":velocity,
        "total_points":total_points,
        "ideal_iterations":int(math.ceil(total_points/velocity)),
        "predicted_iterations":len(predictions),
        "unsized_stories":unsized_stories,
        "carry_over": carry_over,
        "iteration_length":iteration_length
    }, context_instance=RequestContext(request))


def record_prediction(predictions, stories,iteration_number,start_date,iteration_length,points_left):
    points = 0
    for story in stories:
        points += story.points_value()
    predictions.append( { "carried":points_left, "stories":stories , "points":points, "num":iteration_number, "start":start_date, "end":(start_date +  datetime.timedelta(days=(iteration_length-1))) } )

@login_required
def export_project(request, group_slug):    
    project = get_object_or_404(Project, slug=group_slug)
    read_access_or_403(project, request.user )
    return exportProject( project )
    # if request.method == "POST":
    #     form = ExportProjectForm( request.POST )
    #     if form.is_valid():
    #         return exportProject( project, form.cleaned_data["format"])
    #     else:
    #         return HttpResponseRedirect(reverse("project_detail",kwargs={'group_slug':project.slug}))
    # else:
    #     form = ExportProjectForm()
    # return render_to_response("projects/project_export_options.html", { "project":project, "form":form }, context_instance=RequestContext(request))
