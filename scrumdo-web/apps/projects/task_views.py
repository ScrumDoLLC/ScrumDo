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
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


from django.conf import settings

import re


from projects.models import Task, Story
from projects.forms import *
from projects.access import *
import projects.signals as signals

import logging

logger = logging.getLogger(__name__)

# View called via ajax on the iteration or iteration planning pages.  Meant to add one new task
@login_required
def create_task( request ):
    if request.method != "POST":
        return HttpResponseNotAllowed('Only POST allowed')        
    story_id = request.POST.get("story_id")
    story = get_object_or_404( Story, id=story_id )
    write_access_or_403( story.project, request.user )
    task_text = request.POST.get("summary")
    logger.debug("Adding task to story %d %s" % (story.id, task_text) )
    
    task = Task(story=story, summary=task_text)
    task.save()
    
    return render_to_response("stories/single_block_story.html", {
        "story": story,
      }, context_instance=RequestContext(request))

