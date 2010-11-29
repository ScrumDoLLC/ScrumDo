from django import template
from projects.forms import ProjectForm
from projects.access import has_write_access, has_admin_access
register = template.Library()

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
