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

from django.conf.urls.defaults import *

from organizations.models import Organization, Team


# from groups.bridge import ContentBridge
#
#
# bridge = ContentBridge(Project, 'projects')

urlpatterns = patterns('organizations.views',
    url(r'^debug/$', "team_debug"),
    url(r'^create/$', 'organization_create', name="organization_create"),
    url(r'^(?P<organization_slug>[-\w]+)/$', 'organization', name="organization_detail"),
    url(r'^(?P<organization_slug>[-\w]+)/edit$', 'organization_edit', name="organization_edit"),
    url(r'^(?P<organization_slug>[-\w]+)/export$', 'export_organization', name="export_organization"),
    url(r'^(?P<organization_slug>[-\w]+)/delete$', 'delete_organization', name="delete_organization"),
    
)


urlpatterns += patterns('organizations.team_views',
   url(r'^(?P<organization_slug>[-\w]+)/team/create$', 'team_create', name="team_create"),
   url(r'^(?P<organization_slug>[-\w]+)/team/(?P<team_id>[0-9]+)/delete$', 'team_delete', name="team_delete"),
)
