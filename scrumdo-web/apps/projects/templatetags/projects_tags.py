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
from datetime import date
from projects.forms import ProjectForm
from projects.models import Story
from projects.access import has_write_access, has_admin_access, has_read_access
from projects.util import reduce_burndown_data
from django.template.defaultfilters import stringfilter



import re
register = template.Library()

urlfinder = re.compile('(http:\/\/[^\s<>]+)')
import logging

logger = logging.getLogger(__name__)

@register.filter("google_chart_url")
def google_chart_url(iteration_or_project):
    try:
        if hasattr(iteration_or_project,"slug"):
            size = "550x100"
        else:
            size = "550x80"
        
        
        total_points = []
        claimed_points = []
        max_val = 0
        for log in iteration_or_project.points_log.all():
            total_points.append( [log.timestamp(), log.points_total] )
            claimed_points.append( [log.timestamp(), log.points_claimed] )
            if log.points_total > max_val: 
                max_val = log.points_total
    
        if len(total_points) <= 1:
            return "cht=lxy&chs=5x5"
        
        total_points = reduce_burndown_data(total_points)
        claimed_points = reduce_burndown_data(claimed_points)
    
        claimed_dates = []
        claimed_values = []
        total_dates = []
        total_values = []
    
        start_date = total_points[0][0]
        end_date = total_points[-1][0]
        start_date_s = date.fromtimestamp( start_date/1000 ).strftime('%Y-%m-%d')
        end_date_s = date.fromtimestamp( end_date/1000 ).strftime('%Y-%m-%d')
    
        date_range = end_date - start_date

        for piece in total_points:
            total_dates.append( _googleChartValue(piece[0], start_date, end_date) )
            total_values.append( _googleChartValue( piece[1] ,0, max_val) )
        
        for piece in claimed_points:
            claimed_dates.append( _googleChartValue(piece[0], start_date, end_date) )
            claimed_values.append( _googleChartValue( piece[1] ,0, max_val) )
        
        data = "http://chart.googleapis.com/chart?chxr=0,0,%d&cht=lxy&chs=%s&chd=s:%s,%s,%s,%s&chxt=y,x&chxs=0,444444,8,0,lt&chxl=1:|%s|%s&chco=9ED147,197AFF&chm=B,7EAEE3,1,0,0|B,99CBB0,0,0,0" % ( max_val,size,"".join(claimed_dates), "".join(claimed_values), "".join(total_dates), "".join(total_values), start_date_s, end_date_s )
        logger.debug(data)
        return data
    except:
        return "cht=lxy&chs=5x5"
        

@register.filter("urlify2")
def urlify2(value):
    return urlfinder.sub(r'<a target="_blank" href="\1">\1</a>', value)

@register.filter("name_or_username")
def name_or_username(user):
    if user.first_name and user.last_name:
        return "%s %s" % (user.first_name, user.last_name)
    return user.username

@register.filter("probable_email")
def probable_email(user):
    if len(user.email) > 0:
        return user.email
    addrs = user.emailaddress_set.all()
    for email in addrs:
        if email.verified:
            return email.email

    # no verified, no primary emails...
    if len(addrs) > 0:
        return addrs[0].email

    return ""

@register.filter
def gt(a, b):
    return a > b
    
    
@stringfilter
def link_stories(value, project):

    def replaceLink( value ):
        try:
            local_id = value.group(1)
            story = Story.objects.get( project=project, local_id=int(local_id) )
            return "<a class='storyLink' onclick=\"jQuery.facebox({ ajax: '/projects/project/%s/story/%d?return_type=block'}); return false;\" >%s</a>" % (project.slug, story.id, value.group(0))
        except:
            return value.group(0)

    return re.sub(r'[sS]tory #([0-9]+)', replaceLink , value)

link_stories.is_safe=True

# <a onclick="jQuery.facebox({ ajax: '/projects/project/{{ story.project.slug }}/story/{{ story.id }}?return_type=mini'}); return false;" href="/project/{{ story.project.slug }}/story/{{ story.id }}"><img title="Story Details" src="/site_media/static/pinax/images/silk/icons/magnifier.png" /></a>
register.filter('link_stories', link_stories)


@register.inclusion_tag("projects/project_item.html", takes_context=True)
def show_project(context, project):
    return {'project': project, 'request': context['request']}

# @@@ should move these next two as they aren't particularly project-specific

@register.simple_tag
def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path


@register.simple_tag
def persist_getvars(request):
    getvars = request.GET.copy()
    if len(getvars.keys()) > 0:
        return "?%s" % getvars.urlencode()
    return ''

@register.tag(name="notlocked")
def isNotLocked(parser, token):
    tag_name, story = token.split_contents()
    nodelist = parser.parse(('endnotlocked',))
    parser.delete_first_token()
    return NotLockedNode(nodelist, story)

class NotLockedNode(template.Node):
    def __init__(self, nodelist, story):
        self.nodelist = nodelist
        self.story = story
    def render(self, context):
        if not context[self.story].iteration.locked:
            output = self.nodelist.render(context)
            return output
        else:
            return ""

@register.tag(name="locked")
def istLocked(parser, token):
    tag_name, story = token.split_contents()
    nodelist = parser.parse(('endlocked',))
    parser.delete_first_token()
    return LockedNode(nodelist, story)

class LockedNode(template.Node):
    def __init__(self, nodelist, story):
        self.nodelist = nodelist
        self.story = story
    def render(self, context):
        if context[self.story].iteration.locked:
            output = self.nodelist.render(context)
            return output
        else:
            return ""

@register.tag(name="isadmin")
def isadmin( parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endisadmin',))
    parser.delete_first_token()
    return IsAdminNode(nodelist, project)

class IsAdminNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist
        self.project = project
    def render(self, context):
        if has_admin_access(context[self.project], context["request"].user):
            output = self.nodelist.render(context)
            return output
        else:
            return ""


@register.tag(name="canwrite")
def canwrite( parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endcanwrite',))
    parser.delete_first_token()
    return CanWriteNode(nodelist, project)

class CanWriteNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist
        self.project = project
    def render(self, context):
        if has_write_access(context[self.project], context["request"].user):
            output = self.nodelist.render(context)
            return output
        else:
            return ""


@register.tag(name="canread")
def canread( parser, token):
    tag_name, project = token.split_contents()
    nodelist = parser.parse(('endcanread',))
    parser.delete_first_token()
    return CanReadNode(nodelist, project)

class CanReadNode(template.Node):
    def __init__(self, nodelist, project):
        self.nodelist = nodelist
        self.project = project
    def render(self, context):
        if has_read_access(context[self.project], context["request"].user):
            output = self.nodelist.render(context)
            return output
        else:
            return ""


def _googleChartValue(val, min_val, max_val):
    codes = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    percent = (val-min_val) / float(max_val - min_val) 
    #logger.debug("%d %d %d %f" % (val,min_val,max_val,percent))
    new_val = int( 61 * percent )
    return codes[ new_val ]
    



