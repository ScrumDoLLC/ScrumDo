from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.feeds import Feed
from django.shortcuts import get_object_or_404
from projects.models import Project, ProjectMember, Iteration, Story
from activities.models import SubjectActivity

class ProjectStories(Feed):
    def get_object(self,primarykey):
        if len(primarykey) != 1:
            raise ObjectDoesNotExist
        project = get_object_or_404(Project, pk=primarykey[0])
        return project

    def title(self, obj):
        return "Scrumdo Project %s." % obj.name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def item_link(self, obj):
        return obj.story.iteration.get_absolute_url()

    def description(self, obj):
        return "Recent work in all iterations of project."
 
    def items(self, obj):
        activities = SubjectActivity.objects.filter(story__project = obj)
        return activities[:30]


class ProjectCurrentStories(ProjectStories):
    def description(self, obj):
        return "Recent work in current iteration of project."
 
    def items(self, obj):
        iterations = obj.get_current_iterations()
        activities = []
        for iteration in iterations:
            activities.extend(SubjectActivity.objects.filter(story__iteration=iteration))
        return activities[:30]


class ProjectIterationStories(Feed):
    def get_object(self,project_and_iteration):
        if len(project_and_iteration) != 2:
            raise ObjectDoesNotExist
        project = get_object_or_404(Project, pk=project_and_iteration[0])
        iteration = get_object_or_404(Iteration, pk=project_and_iteration[1])
        return (project,iteration)

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
        activities = SubjectActivity.objects.filter(story__iteration=obj[1])
        return activities
