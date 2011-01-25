from django import template
from activities.models import Activity, StoryActivity, IterationActivity

register = template.Library()


@register.filter
def activity_action(activity):
    if isinstance(activity,StoryActivity) and activity.storyactivity.status:
        return (activity.action.name + " to " + activity.storyactivity.status)
    else:
        return activity.action.name

@register.filter
def activity_object(activity):
    if isinstance(activity,StoryActivity):
        return ("Story " + activity.story.summary)
    elif isinstance(activity,IterationActivity):
        return ("Iteration " + activity.iteration.name)
    else:
        return ("Project " + activity.project.slug)

@register.filter
def activity_context(activity):
    return ("Project " + activity.project.name)
