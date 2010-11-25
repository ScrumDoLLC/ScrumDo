from django import template
from projects.forms import ProjectForm

register = template.Library()

# Spits out the iteration name as a link prefixed with the correct icon
@register.inclusion_tag('projects/iteration_name.html', takes_context=True)
def iteration_name(context, iteration):
    return {'iteration': iteration, 'request': context['request']}
    
    