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

register = template.Library()

# Spits out the iteration name as a link prefixed with the correct icon
@register.inclusion_tag('projects/iteration_name.html', takes_context=True)
def iteration_name(context, iteration):
    return {'iteration': iteration, 'request': context['request']}


# Spits out the iteration icon
@register.inclusion_tag('projects/iteration_icon.html', takes_context=True)
def iteration_icon(context, iteration):
    return {'iteration': iteration, 'request': context['request']}
