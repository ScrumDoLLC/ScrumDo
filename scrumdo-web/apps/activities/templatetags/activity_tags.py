from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape


from activities.models import Activity, StoryActivity, IterationActivity, DeletedActivity, CommentActivity, PointsChangeActivity

register = template.Library()

def iteration_name(iteration):
    if iteration.name == "Backlog":
        return "Backlog"
    else:
        return "Iteration %s" % iteration.name

def iteration_uri(iteration, project):
    return reverse("iteration", args=[project.slug, iteration.id])

def iteration_link(iteration, project):
    return ("<a href='%s'>" % iteration_uri(iteration, project)) + iteration_name(iteration) + "</a>"

def story_link(s, project):
    return ("<a href='%s#story_%s'>" % (iteration_uri(s.iteration, project), s.id)) + escape(s.summary) + "</a>"




@register.filter
def activity_action(activity):
    if isinstance(activity,StoryActivity) and activity.status:
        return (activity.action.name + " to " + activity.status + " for ")
    elif isinstance(activity,IterationActivity) and activity.numstories:
        return activity.action.name + " " + str(activity.numstories) + " stories"
    else:
        return activity.action.name

@register.filter
def activity_object(activity):
    if isinstance(activity,StoryActivity):
        s = activity.story
        return mark_safe(story_link(s, activity.project) + " in " + iteration_link(s.iteration, activity.project))
    elif isinstance(activity,IterationActivity):
        if activity.numstories:
            # this is a reorder activity
            start = "in "
        else:
            start = ""
        return mark_safe(start + iteration_link(activity.iteration, activity.project))
    elif isinstance(activity,DeletedActivity):
        return mark_safe(activity.name)
    elif isinstance(activity,CommentActivity):
        return mark_safe("<em>" + escape(activity.comment) + "</em>")
    elif isinstance(activity,PointsChangeActivity):
        return mark_safe("from <strong>" + escape(activity.old) + "</strong> to <strong>" + escape(activity.new) + "</strong> for " + story_link(activity.story, activity.project))
    else:
        return mark_safe("<a href='%s'>" % (reverse("project_detail", args=[activity.project.slug])) + activity.project.name + "</a>")

@register.filter
def activity_context(activity):
    if isinstance(activity,IterationActivity) and activity.numstories:
        start = "of "
    if isinstance(activity,CommentActivity):
        start = "on " + story_link(activity.story, activity.project) + " in "
    else:
        start = "in "
    return mark_safe(start + "<a href='%s'>" % (reverse("project_detail", args=[activity.project.slug])) + activity.project.name + "</a>")
