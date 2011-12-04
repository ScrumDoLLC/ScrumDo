from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.feeds import Feed
from django.shortcuts import get_object_or_404
from projects.models import Project, ProjectMember, Iteration, Story
from activities.models import NewsItem

import activities.feedgenerator as feedgenerator

import logging

logger = logging.getLogger(__name__)

# 
# class OrganizationStories(Feed):
# 
#     def __init__(self, slug, request):
#         self.feed_type = feedgenerator.DefaultFeed
#         self.slug = slug
#         self.request = request
#         self.feed_url = self.feed_url or request.path
#         self.title_template_name = self.title_template or ('feeds/%s_title.html' % slug)
#         self.description_template_name = self.description_template or ('feeds/%s_description.html' % slug)
# 
# 
#     def get_object(self,key_and_token):
#         if len(key_and_token) != 2:
#             raise FeedDoesNotExist
#         project = get_object_or_404(Project, pk=key_and_token[0])
#         if project.token == key_and_token[1]:
#             return project
#         else:
#             return None
# 
#     def item_pubdate(self, item):
#         # Returning the time the action was created, lets RSS readers sort them properly.
#         return item.created
# 
#     def title(self, obj):
#         return "Scrumdo - %s" % obj.name
# 
#     def link(self, obj):
#         if not obj:
#             raise FeedDoesNotExist
#         return obj.get_absolute_url()
# 
#     def item_enclosure_url(self, item):
#         try:
#             return obj.get_absolute_url()
#         except:
#             return ""
# 
#     def item_link(self, obj):
#         try:
#             return obj.get_absolute_url()
#         except:
#             return ""
# 
#     def item_guid(self, obj):
#         # We need to return unique GUIDs for each activity, or RSS readers will assume they're the same entry
#         return "GUID-%d" % obj.id
# 
#     def description(self, obj):
#         return "Recent work in all iterations of project."
# 
#     def items(self, obj):
#         if not obj.active:
#             return []
#         activities = NewsItem.objects.filter(project = obj)
#         return activities[:60]

class ProjectStories(Feed):

    def __init__(self, slug, request):
        self.feed_type = feedgenerator.DefaultFeed
        self.slug = slug
        self.request = request
        self.feed_url = self.feed_url or request.path
        self.title_template_name = self.title_template or ('feeds/%s_title.html' % slug)
        self.description_template_name = self.description_template or ('feeds/%s_description.html' % slug)


    def get_object(self,key_and_token):
        if len(key_and_token) != 2:
            raise FeedDoesNotExist
        project = get_object_or_404(Project, pk=key_and_token[0])
        if project.token == key_and_token[1]:
            return project
        else:
            return None

    def item_pubdate(self, item):
        # Returning the time the action was created, lets RSS readers sort them properly.
        return item.created

    def title(self, obj):
        return "Scrumdo - %s" % obj.name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def item_enclosure_url(self, item):
        try:
            return obj.get_absolute_url()
        except:
            return ""

    def item_link(self, obj):
        try:
            return obj.get_absolute_url()
        except:
            return ""

    def item_guid(self, obj):
        # We need to return unique GUIDs for each activity, or RSS readers will assume they're the same entry
        return "GUID-%d" % obj.id

    def description(self, obj):
        return "Recent work in all iterations of project."

    def items(self, obj):
        if not obj.active:
            return []
        activities = NewsItem.objects.filter(project = obj)
        return activities[:60]

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

    def title(self, obj):
        return "Scrumdo - %s - Current Iteration" % obj.name

    def items(self, obj):
        iterations = obj.get_current_iterations()
        return getIterationsStories(iterations)

class ProjectIterationStories(Feed):

    def __init__(self, slug, request):
        self.feed_type = feedgenerator.DefaultFeed
        self.slug = slug
        self.request = request
        self.feed_url = self.feed_url or request.path
        self.title_template_name = self.title_template or ('feeds/%s_title.html' % slug)
        self.description_template_name = self.description_template or ('feeds/%s_description.html' % slug)

    def get_object(self,project_and_iteration):
        logger.debug( project_and_iteration )
        if len(project_and_iteration) != 3:
            raise ObjectDoesNotExist
        project = get_object_or_404(Project, pk=project_and_iteration[0])
        if project.token == project_and_iteration[1]:
            iteration = get_object_or_404(Iteration, pk=project_and_iteration[2])
            return (project,iteration)
        else:
            return None

    def item_guid(self, obj):
        # We need to return unique GUIDs for each activity, or RSS readers will assume they're the same entry
        return "GUID-%d" % obj.id

    def title(self, obj):
        return "Scrumdo - %s / %s" % (obj[0].name, obj[1].name)

    def link(self, obj):
        if not obj[0]:
            raise FeedDoesNotExist
        return obj[0].get_absolute_url()

    def item_link(self, obj):
        try:
            return obj.story.iteration.get_absolute_url()
        except:
            return obj.iteration.get_absolute_url()

    def description(self, obj):
        return "Stories in Iteration %s of project." % obj[1].name

    def items(self, obj):
        return getIterationsStories([obj[1]])
