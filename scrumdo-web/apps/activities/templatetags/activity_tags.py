from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from activities.models import Activity, StoryActivity, IterationActivity

register = template.Library()


@register.filter
def activity_action(activity):
    if isinstance(activity,StoryActivity) and activity.storyactivity.status:
        return (activity.action.name + " to " + activity.storyactivity.status + " for ")
    else:
        return activity.action.name

@register.filter
def activity_object(activity):
    if isinstance(activity,StoryActivity):
        return mark_safe("<a href='%s#story_%s'>" % (reverse("iteration", args=[activity.project.slug, activity.story.iteration.id]), activity.story.id) + activity.story.summary + "</a>")
        return ("Story " + activity.story.summary)
    elif isinstance(activity,IterationActivity):
        return mark_safe("<a href='%s'>Iteration " % (reverse("iteration", args=[activity.project.slug, activity.iteration.id])) + activity.iteration.name + "</a>")
    else:
        return mark_safe("<a href='%s'>" % (reverse("project_detail", args=[activity.project.slug])) + activity.project.name + "</a>")

@register.filter
def activity_context(activity):
        return mark_safe("<a href='%s'>" % (reverse("project_detail", args=[activity.project.slug])) + activity.project.name + "</a>")
