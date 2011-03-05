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
import re
register = template.Library()

@register.simple_tag
def task_counts( story):
    total_tasks = story.tasks.count()
    complete_tasks = story.tasks.filter(complete=True).count()    
    if complete_tasks > 0:
        return "%d/%d" % (complete_tasks, total_tasks)
    elif total_tasks > 0:
        return "%d" % (total_tasks)
    else:
        return ""