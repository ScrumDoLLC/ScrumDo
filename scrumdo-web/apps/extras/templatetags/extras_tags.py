# From: https://github.com/darkpixel/irontickets/blob/master/irontickets/templatetags/ifloaded.py

from django.conf import settings
from django import template
from django.template import NodeList

from extras.manager import manager as extras_manager

register = template.Library()

import logging

logger = logging.getLogger(__name__)

@register.filter(name='extra_name')
def extra_name( slug ):
    extra = extras_manager.getExtra( slug )
    return extra.getName()

@register.inclusion_tag('extras/extras_buttons.html')
def extra_buttons(extra_slug, projectOrIteration):
    try:
        if hasattr(projectOrIteration,"project"):
            project = projectOrIteration.project
            iteration = projectOrIteration
        else:
            project = projectOrIteration
            iteration = None
        extra = extras_manager.getExtra( extra_slug )

        return {'extra':extra, 'project':project, 'actions':extra.getExtraActions(project, iteration=iteration)}
    except:
        return {}


@register.inclusion_tag('extras/extras_story_buttons.html')
def extra_story_buttons(extra_slug, story):
    extra = extras_manager.getExtra( extra_slug )
    return {'extra':extra, 'actions':extra.getExtraStoryActions(story.project, story)}


@register.tag(name='ifloaded')
def do_ifloaded(parser, token):
    bits = token.split_contents()[1:]
    var = bits[0]
    nodelist_true = parser.parse(('else', 'endifloaded'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifloaded',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfLoadedNode(var, nodelist_true, nodelist_false)



class IfLoadedNode(template.Node):
    def __init__(self, var, nodelist_true, nodelist_false=None):
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.var = var

    def __repr__(self):
        return '<IfLoaded node>'

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.nodelist_true.get_nodes_by_type(nodetype))
        nodes.extend(self.nodelist_false.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        for app in settings.INSTALLED_APPS:
            if str(app) == str(self.var):
                return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)
