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
# License along with this library;  if not, write to the Free Software
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

from haystack.query import SearchQuerySet

from util import reduce_burndown_data

import json
import datetime
import math
import logging
import time

from projects.calculation import onDemandCalculateVelocity
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
# For logged in users:
#   If they have a single organization, it redirects them there.
#   If they have multiple organizations, it prompts to select one
#   If they have no organization, it suggests they create one or ask to join one.
def home( request ):
    my_projects = [];
    member_projects = [];
    organizations = [];
    next_page = False

    if request.user.is_authenticated():
        organizations = Organization.getOrganizationsForUser(request.user)
        if len(organizations) == 1:
            return HttpResponseRedirect(organizations[0].get_absolute_url())

        return render_to_response("homepage.html", {
           "my_organizations": organizations,
           "now": datetime.datetime.now()
          }, context_instance=RequestContext(request))
    else:
        return render_to_response("unauthenticated_homepage.html", context_instance=RequestContext(request))

def usage(request):
    if request.user.is_anonymous():
        organizations = None
    else:
        organizations = Organization.getOrganizationsForUser( request.user )

    return render_to_response("usage_restrictions.html", {"organizations":organizations}, context_instance=RequestContext(request))

def remove_user( request, group_slug ):
    project = get_object_or_404( Project, slug=group_slug )
    admin_access_or_403(project, request.user )
    user_id = int(request.POST.get("user_id"))
    # logger.debug("Removing user %d from project %s" % (user_id, group_slug))
    membership = project.members.get( user__id=user_id )
    membership.delete()
    return HttpResponse("ok")

@login_required
def search_project(request, group_slug):
    project = get_object_or_404( Project, slug=group_slug )
    search_terms = request.GET.get("q","")
    read_access_or_403(project, request.user )
    if search_terms == "":
        search_results = SearchQuerySet().filter(project_id=project.id).models(Story).order_by("rank").load_all()
    else:
        search_results = SearchQuerySet().filter(project_id=project.id).filter(content=search_terms).models(Story).order_by("rank").load_all()
    organization = _organizationOrNone(project)
    return render_to_response("projects/search_results.html", 
                              {
                                "project":project,
                                "search_terms":search_terms,
                                "organization":organization,
                                "search_results":search_results
                              },
                              context_instance=RequestContext(request))

    

@login_required
def epics(request, group_slug):
    project = get_object_or_404( Project, slug=group_slug )
    archived = request.GET.get("show_archived","false") == "true"
    read_access_or_403(project, request.user )
    epics = project.epics.filter(parent__isnull=True)
    if not archived:
        epics = epics.filter(archived=False)
    first_time = len(epics) == 0
    epics_list = _flattenEpics(epics)
    organization = _organizationOrNone(project)
    add_story_form = handleAddStory(request, project)
    add_epic_form = EpicForm(project)

    return render_to_response("projects/epics.html", 
                              {
                                "project":project,
                                "epic_list":epics_list,
                                "organization":organization,
                                "add_story_form":add_story_form,
                                "add_epic_form":add_epic_form,
                                "archived":archived,
                                "first_time":first_time
                              },
                              context_instance=RequestContext(request))

def _flattenEpics(epics):
    """You need to flatten out a tree structure before passing it to the Django template engine, because
       templates can't recurse."""

    yield 'in'

    for epic in epics:
      yield epic
      subepics = epic.children.all()
      if len(subepics):
          epic.leaf=False
          for x in _flattenEpics(subepics):
              yield x
      else:
          epic.leaf=True
    yield 'out'

@login_required
def all_iterations(request, group_slug):
    project = get_object_or_404( Project, slug=group_slug )
    read_access_or_403(project, request.user)
    iterations = project.iterations.all()
    return render_to_response("projects/all_iterations.html", {"iterations":iterations, "project":project}, context_instance=RequestContext(request))
    
@login_required
def activate( request, group_slug ):
    project = get_object_or_404( Project, slug=group_slug )
    admin_access_or_403(project, request.user, ignore_active=True)
    project.active = True
    project.save()
    return HttpResponseRedirect( reverse("project_detail", kwargs={"group_slug":project.slug} ) )

@login_required
def iteration_list(request, group_slug):
    project = get_object_or_404( Project, slug=group_slug )
    admin_access_or_403(project, request.user, ignore_active=True)
    return render_to_response("projects/iteration_list_ajax.html", {"project":project}, context_instance=RequestContext(request))


# The project admin page, this is where you can change the title, description, etc. of a project.
@login_required
def project_admin( request, group_slug ):
    project = get_object_or_404( Project, slug=group_slug )

    admin_access_or_403(project, request.user )

    form = ProjectOptionsForm(instance=project)
    adduser_form = AddUserForm(project=project, user=request.user)

    if request.method == 'POST': # If one of the three forms on the page has been submitted...
        if request.POST.get("action") == "updateProject":
            form = ProjectOptionsForm( request.POST, instance=project)
            if form.is_valid(): # All validation rules pass
                form.save()
                request.user.message_set.create(message="Project options Saved.")
                return HttpResponseRedirect(reverse("project_detail",kwargs={'group_slug':project.slug}))
        if request.POST.get("action") == "moveToOrganization":
            organization = get_object_or_404( Organization, id=request.POST.get("organization_id",""))
            if project.organization:
                for team in project.organization.teams.all():
                    if project in team.projects.all():
                        team.projects.remove(project)                
            project.organization = organization
            project.save()
            owners = organization.getOwnersGroup()
            if owners:
                owners.projects.add(project)
            request.user.message_set.create(message="Project moved to organization")
            return HttpResponseRedirect(reverse("organization_detail",kwargs={'organization_slug':organization.slug}))
        # if request.POST.get("action") == "removeFromOrganization":
        #     if request.POST.get("remove") == "on":
        #         for team in project.organization.teams.all():
        #             if project in team.projects.all():
        #                 team.projects.remove(project)
        #         project.organization = None
        #         project.save()
        #         request.user.message_set.create(message="Project removed from organization")
        if request.POST.get("action") == "add":
            write_access_or_403(project, request.user )
            adduser_form = AddUserForm(request.POST, project=project, user=request.user)
            if adduser_form.is_valid():
                adduser_form.save(request.user)
                return HttpResponseRedirect( reverse("project_admin", kwargs={"group_slug":project.slug} ) )
        if request.POST.get("action") == "archiveProject":
            project.active = False
            project.save()
            return HttpResponseRedirect( reverse("project_detail", kwargs={"group_slug":project.slug} ) )






    organizations = Organization.getAdminOrganizationsForUser(request.user)

    return render_to_response("projects/project_admin.html", {
        "project": project,
        "form": form,
        "adduser_form": adduser_form,
        "organizations": organizations
      }, context_instance=RequestContext(request))


# Returns a JSON feed for a given project/iteration that can be transformed with some javascript
# into a burn up chart.
@login_required
def iteration_burndown(request, group_slug, iteration_id):
    project = get_object_or_404( Project, slug=group_slug )
    read_access_or_403(project, request.user )
    iteration = get_object_or_404( Iteration, id=iteration_id )
    if iteration.start_date:
        start_date_timestamp = int((time.mktime(iteration.start_date.timetuple()) - time.timezone)*1000)
    if iteration.end_date:
        end_date_timestamp = int((time.mktime(iteration.end_date.timetuple()) - time.timezone)*1000)
    has_startdate_data = False
    has_enddate_data = False
    highest_total_points = 0
    last_total_points = 0

    total_points = [];
    claimed_points = [];

    for log in iteration.points_log.all():
        
        if iteration.start_date:
            if log.timestamp() != start_date_timestamp and not has_startdate_data :
                total_points.append( [start_date_timestamp, 0])
                claimed_points.append( [start_date_timestamp, 0])
        has_startdate_data = True
        last_total_points = log.points_total
        if iteration.end_date:
            if log.timestamp() == end_date_timestamp :
                has_enddate_data = True
        if highest_total_points < log.points_total:
            highest_total_points = log.points_total
        total_points.append( [log.timestamp(), log.points_total] );
        claimed_points.append( [log.timestamp(), log.points_claimed] );
    if not has_enddate_data and iteration.end_date:
        total_points.append( [end_date_timestamp, highest_total_points])
        
    if iteration.start_date:
        total_points = filter(lambda x:x[0]>=start_date_timestamp, total_points)
        claimed_points = filter(lambda x:x[0]>=start_date_timestamp, claimed_points)
    if iteration.end_date:
        total_points = filter(lambda x:x[0]<=end_date_timestamp, total_points)
        claimed_points = filter(lambda x:x[0]<=end_date_timestamp, claimed_points)

    total_stats = { "label":"Total Points", "data":reduce_burndown_data(total_points)}
    claimed_stats = { "label":"Claimed Points", "data":reduce_burndown_data(claimed_points)}

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

    total_stats = { "label":"Total Points", "data":reduce_burndown_data(total_points)}
    claimed_stats = { "label":"Claimed Points", "data":reduce_burndown_data(claimed_points)}


    json_serializer = serializers.get_serializer("json")()
    result = json.dumps([ total_stats , claimed_stats ])
    return HttpResponse(result) #, mimetype='application/json'




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
    admin_teams = organization.teams.filter(access_type="staff")
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

    add_story_form = handleAddStory(request, project)


    return render_to_response(template_name, {
        "project_form": project_form,
        "add_story_form": add_story_form,
        "project": project,
        "group": project, # @@@ this should be the only context var for the project
        "is_member": is_member,
        "current_view":"project_page",
    }, context_instance=RequestContext(request))

# @login_required
# def burnup_chart(request, group_slug):
#     project = get_object_or_404(Project, slug=group_slug)
#     read_access_or_403(project, request.user )
#     # CairoPlot
#     # data = CairoPlot.dot_line_plot('dotline1_dots', [(1,2),(2,3),(3,3)], 400, 300, axis = True, grid = True, dots = True)
#     response = HttpResponse(data, mimetype="image/png")
#     return response




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
    #return exportProject( project )
    if request.method == "POST":
        form = ExportProjectForm( request.POST )
        if form.is_valid():
            return exportProject( project, form.cleaned_data["file_name"])
        else:
            return HttpResponseRedirect(reverse("project_detail",kwargs={'group_slug':project.slug}))
    else:
        form = ExportProjectForm(initial={'file_name':u'project'})
    return render_to_response("projects/project_export_options.html", { "project":project, "form":form }, context_instance=RequestContext(request))

# @login_required
# def add_category(request, group_slug):
#     project = get_object_or_404(Project, slug=group_slug)
#     read_access_or_403(project, request.user )    
#     name = request.POST.get("category_name")
#     name = name.replace(",","").strip()
#     if not name in project.getCategoryList():
#         project.categories = "%s, %s" % (project.categories, name)
#         project.save()
#     return HttpResponse(name)

def _organizationOrNone(project):
    try:
        organization = project.organization
    except Organization.DoesNotExist:
        organization = None
    return organization
