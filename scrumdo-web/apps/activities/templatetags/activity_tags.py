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
        if iteration.name.startswith("Iteration") or iteration.name.startswith("Sprint"):
            return iteration.name
        else:
            return "Iteration %s" % iteration.name

def iteration_uri(iteration, project):
        return reverse("iteration", args=[project.slug, iteration.id])

def iteration_link(iteration, project):
    return ("<a href='%s'>" % iteration_uri(iteration, project)) + iteration_name(iteration) + "</a>"

def story_link(s, project):
    url = iteration_uri(s.iteration, project)
    summary = escape(smart_truncate(s.summary,length=40))
    return "<a title='%s' href='%s#story_%s'> #%d %s</a>" % (s.summary,url, s.id, s.local_id, summary )


def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

@register.filter
def subscription_checkbox(project , subscription_list):
    try:
        if project.id in subscription_list:
            return "<input type=\"checkbox\" name=\"subscriptions\" value=\"%d\" checked=\"checked\"> " % project.id
        else:
            return "<input type=\"checkbox\" name=\"subscriptions\" value=\"%d\"> " % project.id
    except:
        return ""

@register.filter
def activity_action(activity):
    try:
        if isinstance(activity,StoryActivity) and activity.status:
            return (activity.action.name + " to " + activity.status )
        elif isinstance(activity,IterationActivity) and activity.numstories:
            return activity.action.name + " " + str(activity.numstories) + " stories"
        else:
            return activity.action.name
    except:
        return ""

@register.filter
def activity_object(activity):
    try:
        if isinstance(activity,StoryActivity):
            s = activity.story
            if activity.status:
                return mark_safe(" for " + story_link(s, activity.project) + " in " + iteration_link(s.iteration, activity.project))
            else:
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
    except:
        return ""

@register.filter
def activity_context(activity):
    try:
        if isinstance(activity,IterationActivity) and activity.numstories:
            start = "of"
        if isinstance(activity,CommentActivity):
            start = "on " + story_link(activity.story, activity.project) + " in"
        else:
            start = "in"
        url = reverse("project_detail", args=[activity.project.slug])
        return mark_safe( "%s <a href='%s'>%s</a>" % (start, url, activity.project.name )  )
    except:
        return ""
