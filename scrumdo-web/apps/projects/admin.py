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


from django.contrib import admin
from projects.models import Project, Iteration, SiteStats, Story, StoryTag
from django.conf import settings


if not "subscription" in settings.INSTALLED_APPS:
    class ProjectAdmin(admin.ModelAdmin):
        list_display = ('name', 'slug', 'creator', 'created')
    admin.site.register(Story)  
    admin.site.register(Project, ProjectAdmin)

admin.site.register(Iteration)
admin.site.register(SiteStats )
admin.site.register(StoryTag )
