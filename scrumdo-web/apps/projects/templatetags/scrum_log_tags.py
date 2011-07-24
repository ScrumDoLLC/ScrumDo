from django import template

register = template.Library()

@register.simple_tag
def scrum_log(project):
    return ""
