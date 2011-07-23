from django import template

register = template.Library()

@register.simple_tag
def activity_log(project):
    return ""
