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
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings
from django.core.exceptions import PermissionDenied

from organizations.forms import *
from organizations.models import *
from activities.models import NewsItem
from projects.models import Project
from favorites.models import *
import projects.access as access
import organizations.signals as signals
import organizations.import_export as import_export

import re
import logging

logger = logging.getLogger(__name__)

@login_required
def organization_dashboard(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    # Organization.objects.filter(slug=organization_slug).select_related('subscription')[0]
        
    if organization.projects.count() == 0:
        return HttpResponseRedirect( reverse("organization_projects",kwargs={"organization_slug":organization_slug}))
    
    organizations = Organization.getOrganizationsForUser( request.user )
    
    favorite_projects = Favorite.objects.filter(user=request.user, project__organization=organization).select_related('project').order_by("-project__active","project__category","project__name")
    favorite_projects = [fav.project for fav in favorite_projects]
    
    stories = Story.getAssignedStories(request.user, organization)


    if not organization.hasReadAccess( request.user ):
        raise PermissionDenied()
    
    return render_to_response("organizations/organization_dashboard.html", {
        "organization": organization,
        "organizations": organizations,
        "favorite_projects": favorite_projects,
        "your_stories": stories,
        "return_type":"queue"
        # "members": members,
        # "projects": projects
      }, context_instance=RequestContext(request))
    
@login_required
def organization_projects(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    organizations = Organization.getOrganizationsForUser( request.user )

    if not organization.hasReadAccess( request.user ):
        raise PermissionDenied()

    teams = []
    for team in organization.teams.all():
        teams.append((team, AddUserForm(team=team)))

    # this used to live in team_views.py, but since the individual teams pages
    # have been consolodated, this post is now from the organization overview page
    if request.method == "POST":
        if not organization.hasStaffAccess( request.user ):
            raise PermissionDenied()
        action = request.POST.get("action")
        team_id = request.POST.get("team_id")
        team = get_object_or_404(Team, id=team_id)
        if action == "addMember":
            adduser_form = AddUserForm(request.POST, team=team)
            if adduser_form.is_valid():
                adduser_form.save(request.user)
                adduser_form=AddUserForm(team=team)
        elif action == "addProject":
            if not request.POST.get("project",None):
                request.user.message_set.create(message="Please select a project to add to this team.")
            else:
                project = get_object_or_404( Project, id=request.POST.get("project") )
                team.projects.add(project)
                team.save()
        elif action == "removeProject":
            project = Project.objects.filter(id=request.POST.get("project_id"))[0]
            team.projects.remove(project)
            team.save()
        elif action == "removeUser":
            user = User.objects.filter(id=request.POST.get("user_id"))[0]
            if user == request.user and team.access_type=="staff":
                request.user.message_set.create(message="Can't remove yourself from the staff group.")
            else:
                team.members.remove(user);
                team.save()

    members = []
    users = []
    member_count = 1

    # for team in organization.teams.all():
    #     for user in team.members.all():
    #         if not user in users:                
    #             users.append(user)
    #             members.append("#%d %s (Team %s)" % (member_count,  user, team.name))
    #             member_count+=1

    projects = organization.projects.all().order_by("-active","category","name")

    # for project in projects:
    #     for member in project.members.all():
    #         if (not member.user in users) and (member.user != project.creator):
    #             users.append(member.user)
    #             members.append("#%d %s (Project %s)" % (member_count, member.user, project.name))
    #             member_count+=1

    return render_to_response("organizations/organization_projects.html", {
        "organization": organization,
        "organization_teams": teams,
        "organizations": organizations,
        "members": members,
        "projects": projects
      }, context_instance=RequestContext(request))


# This is an ajax popup form for editing details of an organization.
@login_required
def organization_edit( request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if request.method == "POST" and organization.creator == request.user:
        form = UpdateOrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            request.user.message_set.create(message="Organization Updated")
            form.save()
        else:
            request.user.message_set.create(message="Could not update organization.")

        return HttpResponseRedirect( reverse("organization_detail",kwargs={"organization_slug":organization.slug}))

    form = UpdateOrganizationForm(instance=organization)
    organizations = Organization.getOrganizationsForUser( request.user )
    return render_to_response("organizations/organization_form.html", {
        "organization": organization,
        "organizations": organizations,
        "form":form
      }, context_instance=RequestContext(request))

def handle_organization_create( form , request, projects):
    organization = form.save( commit=False )
    organization.creator = request.user
    organization.save()


    member_team = Team(organization = organization, name="Members", access_type="write")
    member_team.save()
    
    staff_team = Team(organization = organization, name="Staff", access_type="staff")
    staff_team.save()
    staff_team.members.add(request.user)
    
    
    request.user.message_set.create(message="Organization Created.")
    
    try:
        # Store where this user came from via the google analytics tracking cookie.  Example values:
        # 183024036.1310791887.2.2.utmcsr=freshmeat.net|utmccn=(referral)|utmcmd=referral|utmcct=/projects/scrumdo; 
        # 183024036.1310842365.1.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=scrumdo%20harvest
        # 183024036.1311098060.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)
        # Adwords:
        # 37276784.1312040997.1.1.utmgclid=CPCFncq1qaoCFYne4AodhCvMWw|utmccn=(not%20set)|utmcmd=(not%20set)|utmctr=scrum
        
        cookie = request.COOKIES.get("__utmz")
        if re.search("utmgclid", cookie) == None:
            # Referrer based source
            source = re.search("utmcsr=([^|]+)",cookie).group(1)
            mode = re.search("utmcmd=([^|]+)",cookie).group(1)
            organization.source = "%s / %s" % (source, mode)
        else:
            # Adwords based source?
            source = re.search("utmgclid=([^|]+)",cookie).group(1)
            mode = re.search("utmctr=([^|]+)",cookie).group(1)
            organization.source = "Adwords / %s / %s" % (source, mode)
                
        organization.save()        
    except:
        organization.source = ""
        
    signals.organization_created.send( sender=request, organization=organization )    

    for project in projects:
        if request.POST.get("move_project_%d" % project.id):
            _move_project_to_organization(project, organization, member_team)
            # member_team.projects.add( project )

    return organization

@login_required
def organization_create(request):
    projects = Project.objects.filter(creator=request.user)

    if request.method == 'POST': # If the form has been submitted...
        form = OrganizationForm( request.POST)

        if form.is_valid(): # All validation rules pass
            organization = handle_organization_create(form, request, projects )
            return HttpResponseRedirect(reverse("organization_detail",  kwargs={'organization_slug':organization.slug}))
    else:
        form = OrganizationForm()

    organizations = Organization.getOrganizationsForUser( request.user )

    return render_to_response("organizations/create_organization.html", {
        "organizations": organizations,
        "form": form,
        "projects": projects
      }, context_instance=RequestContext(request))

def _move_project_to_organization(project, organization, member_team):
    project.teams.clear()
    project.organization = organization
    member_team.projects.add(project)

    for membership in project.members.all():
        member = membership.user
        if member != project.creator:
            member_team.members.add( member )
            membership.delete()
    member_team.save()
    project.save()

@login_required
def favorite_all(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    for project in organization.projects.all():
        if project.active and access.has_read_access(project, request.user):
            Favorite.setFavorite( 1, project.id, request.user, True)
    return HttpResponseRedirect( reverse("organization_detail",kwargs={"organization_slug":organization_slug}))
    
@login_required
def team_debug(request):
    read_orgs = Organization.getOrganizationsForUser(request.user)
    admin_orgs = Organization.getAdminOrganizationsForUser(request.user)
    # write_orgs = Organization.getReadWriteOrganizationsForUser(request.user)
    return render_to_response("organizations/team_debug.html", {
        "read_orgs":read_orgs,
        "admin_orgs":admin_orgs,
      }, context_instance=RequestContext(request))

@login_required
def export_organization(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasReadAccess( request.user ):
        raise PermissionDenied()

    organizations = Organization.getOrganizationsForUser( request.user )

    if request.method == "POST":
        projects = []
        for key, value in request.POST.iteritems():
            m = re.match("proj_([0-9]+)",key)
            if m and value:
                projects.append(int(m.group(1)) )
        logger.debug(projects)
        return import_export.export_organization( organization, project_ids=projects)


    return render_to_response("organizations/organization_export.html", {
        "organization":organization,
        "organizations":organizations,
      }, context_instance=RequestContext(request))
    


@login_required
def delete_organization(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    if not organization.hasStaffAccess( request.user ):
        raise PermissionDenied()
    signals.organization_deleted.send( sender=request, organization=organization )
    for project in organization.projects.all():
        project.organization = None
        project.save()
    for team in organization.teams.all():
        team.delete()
    organization.delete()
    return HttpResponse("Deleted")
