from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers
import json
import datetime

import logging

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
from organizations.models import Organization

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


def home( request ):
  my_projects = [];
  member_projects = [];
  organizations = [];
  if request.user.is_authenticated():
    organizations = Organization.getOrganizationsForUser(request.user)
    memberships = ProjectMember.objects.filter( user=request.user )
    for membership in memberships:
      try:
        if( membership.project.creator == request.user):
          member_projects.append(membership.project)
        else:
          my_projects.append( membership.project )
      except:
        pass
    
    
  return render_to_response("homepage.html", {
       "my_projects":my_projects,
       "my_organizations": organizations,
       "member_projects":member_projects
    }, context_instance=RequestContext(request))


@login_required
def project_admin( request, group_slug ):
  project = get_object_or_404( Project, slug=group_slug )

  admin_access_or_403(project, request.user )  
  
  form = ProjectOptionsForm(instance=project)
  
  if request.method == 'POST': # If the form has been submitted...
    form = ProjectOptionsForm( request.POST, instance=project)
    if form.is_valid(): # All validation rules pass      
      story = form.save( commit=False )
      story.local_id = project.stories.count() + 1
      story.project = project
      story.creator = request.user
      story.save()     
      request.user.message_set.create(message="Options Saved.")               
  else:
    form = ProjectOptionsForm( instance=project )
  
  return render_to_response("projects/project_admin.html", {
      "project": project,
      "form": form
    }, context_instance=RequestContext(request))
    
    
@login_required
def iteration_burndown(request, group_slug, iteration_id):
  project = get_object_or_404( Project, slug=group_slug )
  
  read_access_or_403(project, request.user )
  
  iteration = get_object_or_404( Iteration, id=iteration_id )
  
  
  
  total_points = [];
  claimed_points = [];
  total_stats = { "label":"Total Points", "data":total_points}
  claimed_stats = { "label":"Claimed Points", "data":claimed_points}

  for log in iteration.points_log.all():
    total_points.append( [log.timestamp(), log.points_total] );
    claimed_points.append( [log.timestamp(), log.points_claimed] );

  json_serializer = serializers.get_serializer("json")()
  result = json.dumps([total_stats,claimed_stats])
  return HttpResponse(result) #, mimetype='application/json'
  
  
@login_required
def project_burndown(request, group_slug):
  project = get_object_or_404( Project, slug=group_slug )
  read_access_or_403(project, request.user )
  total_points = [];
  claimed_points = [];
  total_stats = { "label":"Total Points", "data":total_points}
  claimed_stats = { "label":"Claimed Points", "data":claimed_points}

  for log in project.points_log.all():
    total_points.append( [log.timestamp(), log.points_total] );
    claimed_points.append( [log.timestamp(), log.points_claimed] );

  json_serializer = serializers.get_serializer("json")()
  result = json.dumps([total_stats,claimed_stats])
  return HttpResponse(result) #, mimetype='application/json'
  
     
@login_required
def project_history( request, group_slug ):
  project = get_object_or_404( Project, slug=group_slug )
  read_access_or_403(project, request.user )
 
  return render_to_response("projects/project_history.html", {
      "project": project,
    }, context_instance=RequestContext(request))   
     
     
@login_required
def create(request, form_class=ProjectForm, template_name="projects/create.html"):
    project_form = form_class(request.POST or None)
    admin_organizations = Organization.getOrganizationsForUser( request.user )
    
    
    if project_form.is_valid():
        project = project_form.save(commit=False)
        project.creator = request.user
        org_id = request.POST.get("organization","none")
        
        project.save()
        if org_id != "none":
          organization = Organization.objects.filter( id=org_id )[0]
          if organization and organization in admin_organizations:
            addProjectToOrganization(project, organization)       
        
        project_member = ProjectMember(project=project, user=request.user)
        project.members.add(project_member)
        project_member.save()        
        
        default_iteration = Iteration( name='Backlog', detail='', default_iteration=True, project=project)
        project.iterations.add(default_iteration)
        default_iteration.save()        
        request.user.message_set.create(message="Project Created")
        if notification:
            # @@@ might be worth having a shortcut for sending to all users
            notification.send(User.objects.all(), "projects_new_project",
                {"project": project}, queue=True)
        return HttpResponseRedirect(project.get_absolute_url())
    
    return render_to_response(template_name, {
        "project_form": project_form,
        "admin_organizations":admin_organizations
    }, context_instance=RequestContext(request))

def addProjectToOrganization( project, organization):
  logger.info("Adding project %s to organization %s" % (project.slug, organization.slug))
  project.organization = organization
  project.save()
  admin_teams = organization.teams.filter(access_type="admin")
  admin_team = admin_teams[0]
  if not admin_team:
    logger.error('Organization %s has no admin team' % organization.slug )
    return
  admin_team.projects.add( project )
  admin_team.save()
    
    

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



@login_required
def projects(request, template_name="projects/projects.html"):
    return your_projects(request, template_name)

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
        redirect_url = reverse('project_list')
    
    # @@@ eventually, we'll remove restriction that project.creator can't leave project but we'll still require project.members.all().count() == 1
    if (request.user.is_authenticated() and request.method == "POST" and
            request.user == project.creator and project.members.all().count() == 1):
        project.delete()
        request.user.message_set.create(message=_("Project %(project_name)s deleted.") % {"project_name": project.name})
        # no notification required as the deleter must be the only member
    
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
        adduser_form = adduser_form_class(request.POST, project=project)
        if adduser_form.is_valid():
            adduser_form.save(request.user)
            adduser_form = adduser_form_class(project=project) # clear form
    else:
        adduser_form = adduser_form_class(project=project)
    
    add_story_form = StoryForm(project)
    
    return render_to_response(template_name, {
        "project_form": project_form,
        "adduser_form": adduser_form,
        "add_story_form": add_story_form,
        "project": project,
        "group": project, # @@@ this should be the only context var for the project
        "is_member": is_member,
    }, context_instance=RequestContext(request))
