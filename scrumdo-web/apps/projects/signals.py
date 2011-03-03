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


import django.dispatch
                                                             
# Signal dispatched when a story is edited. (Not including status changes, see next signal)
# user = who did it, story = the story that changed.
story_updated = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story's status is changed.
# user = who did it, story = the story that changed.
story_status_changed = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story is deleted
# user = who did it, story = the story that changed.
story_deleted = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story is created
# user = who did it, story = the story that changed.
story_created = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a new task is created.
task_created = django.dispatch.Signal(providing_args=["task","user"])

# Signal dispatched when the status (done/not done) of a task changed.
task_status_changed = django.dispatch.Signal(providing_args=["task","user"])

# Signal dispatched when a task is edited
task_updated = django.dispatch.Signal(providing_args=["task","user"])

# Signal dispatched when a task is deleted.
# Note: it's already been deleted when this is dispatched.
task_deleted = django.dispatch.Signal(providing_args=["task","user"])