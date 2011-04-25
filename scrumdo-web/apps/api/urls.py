from django.conf.urls.defaults import *
from tastypie.api import Api
from api.resources import OrganizationResource, TeamResource, ProjectResource, StoryResource, IterationResource, UserResource# , ActivityResource, CommentResource

v1_api = Api(api_name='v1')
v1_api.register(OrganizationResource())
v1_api.register(TeamResource())
v1_api.register(ProjectResource())
v1_api.register(StoryResource())
# v1_api.register(CommentResource())
v1_api.register(IterationResource())
v1_api.register(UserResource())

# v1_api.register(ActivityResource())

urlpatterns = v1_api.urls
