from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.feeds import Feed
from django.shortcuts import get_object_or_404
from projects.models import Project, ProjectMember, Iteration, Story
from activities.models import Activity, StoryActivity, IterationActivity

class ProjectStories(Feed):
    def get_object(self,key_and_token):
        if len(key_and_token) != 2:
            raise FeedDoesNotExist
        project = get_object_or_404(Project, pk=key_and_token[0])
        if project.token == key_and_token[1]:
            return project
        else:
            return None

    def title(self, obj):
        return "Scrumdo Project %s." % obj.name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def item_link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "Recent work in all iterations of project."
 
    def items(self, obj):
        activities = Activity.objects.filter(project = obj)
        return [activity.mergeChildren() for activity in activities[:30]]

def getIterationsStories(iterations):
    activities = []
    for iteration in iterations:
        activities.extend(StoryActivity.objects.filter(story__iteration=iteration))
        activities.extend(IterationActivity.objects.filter(iteration=iteration))
    print activities
    return sorted(activities[:30], lambda a,b: cmp(a.created,b.created))
    


class ProjectCurrentStories(ProjectStories):
    def description(self, obj):
        return "Recent work in current iteration of project."
 
    def items(self, obj):
        iterations = obj.get_current_iterations()
        return getIterationsStories(iterations)

class ProjectIterationStories(Feed):
    def get_object(self,project_and_iteration):
        if len(project_and_iteration) != 3:
            raise ObjectDoesNotExist
        project = get_object_or_404(Project, pk=project_and_iteration[0])
        if project.token == project_and_iteration[1]:
            iteration = get_object_or_404(Iteration, pk=project_and_iteration[2])
            return (project,iteration)
        else:
            return None

    def title(self, obj):
        return "Scrumdo Project %s." % obj[0].name

    def link(self, obj):
        if not obj[0]:
            raise FeedDoesNotExist
        return obj[0].get_absolute_url()

    def item_link(self, obj):
        return obj.story.iteration.get_absolute_url()

    def description(self, obj):
        return "Stories in Iteration %s of project." % obj[1].name
 
    def items(self, obj):
        return getIterationsStories([obj[1]])
