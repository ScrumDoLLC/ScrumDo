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


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


from projects.models import Project, Story, StoryTag, StoryTagging
from projects.access import *
from story_views import handleAddStory

def tag_detail(request, group_slug, tag_name):
    project = get_object_or_404( Project, slug=group_slug )
    
    read_access_or_403(project,request.user)
    tags_list = StoryTag.objects.filter( project=project, name=tag_name )

    stories = []
    for tags in tags_list:
        # TODO: there's a bug somewhere causing duplicate tags to be created
        stories += [ tagging.story for tagging in tags.stories.all() ]
    
    stories = sorted(stories, key=lambda story: story.rank)
    add_story_form = handleAddStory(request, project)

    if len(tags_list) == 0:
        tag = None
    else:
        tag = tags_list[0]

    return render_to_response("projects/tag_page.html", {
        "tag": tag,
        "stories":stories,
        "organization":_organizationOrNone(project),
        "project" : project,
        'add_story_form': add_story_form,
        "current_view":"tags_view"
      }, context_instance=RequestContext(request))

def _organizationOrNone(project):
  try:
      organization = project.organization
  except Organization.DoesNotExist:
      organization = None
  return organization
