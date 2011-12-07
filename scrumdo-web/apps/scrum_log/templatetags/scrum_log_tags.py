from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from projects.models import Project
from scrum_log.forms import ScrumLogForm

register = template.Library()

@register.inclusion_tag('scrum_log/scrum_log.html')
def scrum_log(project):    
    return {"project":project}
