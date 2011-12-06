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


from django import template
from projects.models import Story
from django.utils.safestring import mark_safe
import re
register = template.Library()


@register.filter
def show_points(story):
    points = story.getPointsLabel()
    if points == "Infinite":
        return mark_safe("&infin;")
    else:
        return mark_safe(points)

@register.simple_tag
def summary_view( story, user):
    if story.assignee != user:    
        return '<div style="display:inline" class="project disabled_project">%s  %s</div>' % ( story.summary, story.detail)
    else:
        return '%s  %s' % (story.summary, story.detail)
