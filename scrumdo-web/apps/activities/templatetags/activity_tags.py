from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from activities.models import Activity, StoryActivity, IterationActivity

register = template.Library()


@register.filter
def activity_action(activity):
    if isinstance(activity,StoryActivity) and activity.status:
        return (activity.action.name + " to " + activity.storyactivity.status + " for ")
    elif isinstance(activity,IterationActivity) and activity.numstories:
        return activity.action.name + " " + str(activity.numstories) + " stories"
    else:
        return activity.action.name

@register.filter
def activity_object(activity):
    if isinstance(activity,StoryActivity):
        return mark_safe("<a href='%s#story_%s'>" % (reverse("iteration", args=[activity.project.slug, activity.story.iteration.id]), activity.story.id) + activity.story.summary + "</a>")
    elif isinstance(activity,IterationActivity):
        if activity.numstories:
            # this is a reorder activity
            start = "in "
        else:
            start = ""
        if activity.iteration.name == "Backlog":
            name = "Backlog"
        else:
            name = "Iteration %s" % activity.iteration.name
        return mark_safe(start + "<a href='%s'>" % (reverse("iteration", args=[activity.project.slug, activity.iteration.id])) + name + "</a>")
    else:
        return mark_safe("<a href='%s'>" % (reverse("project_detail", args=[activity.project.slug])) + activity.project.name + "</a>")

@register.filter
def activity_context(activity):
    if isinstance(activity,IterationActivity) and activity.numstories:
        start = "of "
    else:
        start = "in "
    return mark_safe(start + "<a href='%s'>" % (reverse("project_detail", args=[activity.project.slug])) + activity.project.name + "</a>")
