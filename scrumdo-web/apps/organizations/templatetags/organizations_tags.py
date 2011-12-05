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
from projects.forms import ProjectForm
from projects.models import Story
from projects.access import has_write_access, has_admin_access, has_read_access
from django.template.defaultfilters import stringfilter
import re
register = template.Library()



@register.tag(name="isorgstaff")
def isorgstaff( parser, token):
    tag_name, organization = token.split_contents()
    nodelist = parser.parse(('endisorgstaff',))
    parser.delete_first_token()
    return IsAdminNode(nodelist, organization)

class IsAdminNode(template.Node):
    def __init__(self, nodelist, organization):
        self.nodelist = nodelist
        self.organization = organization
    def render(self, context):
        if context[self.organization].hasStaffAccess(context["request"].user):
            output = self.nodelist.render(context)
            return output
        else:
            return ""



@register.tag(name="teammember")
def teammember( parser, token):
    tag_name, team = token.split_contents()
    nodelist = parser.parse(('endteammember',))
    parser.delete_first_token()
    return IsAdminNode(nodelist, team)

class IsTeamMemberNode(template.Node):
    def __init__(self, nodelist, team):
        self.nodelist = nodelist
        self.team = team
    def render(self, context):
        if context[self.team].hasMember( context["request"].user ):
            output = self.nodelist.render(context)
            return output
        else:
            return ""
            
