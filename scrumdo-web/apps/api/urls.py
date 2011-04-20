from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from api.handlers import ProjectHandler,IterationHandler,StoryHandler,NewsfeedHandler

auth = HttpBasicAuthentication(realm="ScrumDo Test Auth")
ad = { 'authentication': auth }

project_handler = Resource(ProjectHandler, **ad)
iteration_handler = Resource(IterationHandler, **ad)
story_handler = Resource(StoryHandler, **ad)
newsfeed_handler = Resource(NewsfeedHandler, **ad)

urlpatterns = patterns('',
   url(r'^projects/mine', project_handler, {"user" : True}),
   url(r'^projects/organization/(?P<slug>[^/]+)/', project_handler, {"org" : True}),
   url(r'^projects/', project_handler),
   url(r'^project/(?P<slug>[^/]+)/iteration/(?P<iteration_id>[^/]+)/stories', story_handler),
   url(r'^project/(?P<slug>[^/]+)/iteration', iteration_handler),
   url(r'^project/(?P<slug>[^/]+)/story/create', story_handler),
   url(r'^project/(?P<slug>[^/]+)/story/(?P<story_id>[^/]+)/delete', story_handler),
   url(r'^project/(?P<slug>[^/]+)/story/(?P<story_id>[^/]+)/comment', story_handler),
   url(r'^project/(?P<slug>[^/]+)/', project_handler),
   url(r'^newsfeed/(?P<num>[^/]+)', newsfeed_handler),
   url(r'^newsfeed/', newsfeed_handler),
)
