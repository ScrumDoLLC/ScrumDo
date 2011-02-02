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
    def iteration_name(iteration):
        if iteration.name == "Backlog":
            return "Backlog"
        else:
            return "Iteration %s" % iteration.name
    def iteration_link(iteration):
        return reverse("iteration", args=[iteration.project.slug, iteration.id])
    if isinstance(activity,StoryActivity):
        if activity.action.name == "deleted":
            return mark_safe(activity.story_name)
        else:
            s = activity.story
            return mark_safe(("<a href='%s#story_%s'>" % (iteration_link(s.iteration), s.id)) + s.summary + ("</a> in <a href='%s'>" % iteration_link(s.iteration)) + iteration_name(s.iteration) + "</a>")
    elif isinstance(activity,IterationActivity):
        if activity.numstories:
            # this is a reorder activity
            start = "in "
        elif activity.action.name == "deleted":
            return mark_safe(activity.iteration_name)
        else:
            start = ""
        return mark_safe(start + "<a href='%s'>" % (reverse("iteration", args=[activity.project.slug, activity.iteration.id])) + iteration_name(activity.iteration) + "</a>")
    else:
        return mark_safe("<a href='%s'>" % (reverse("project_detail", args=[activity.project.slug])) + activity.project.name + "</a>")

@register.filter
def activity_context(activity):
    if isinstance(activity,IterationActivity) and activity.numstories:
        start = "of "
    else:
        start = "in "
    return mark_safe(start + "<a href='%s'>" % (reverse("project_detail", args=[activity.project.slug])) + activity.project.name + "</a>")
