from django.conf.urls.defaults import *
from tastypie.api import Api
from api.resources import *

class ScrumDoApi(Api):
    def override_urls(self):
        return [url(r'^v1/login$', "api.views.login" , name="api_login"),
                url(r'^v1/is_key_valid$', "api.views.is_key_valid" , name="is_key_valid"),
                ]

v1_api = ScrumDoApi(api_name='v1')
v1_api.register(OrganizationResource())
v1_api.register(TeamResource())
v1_api.register(ProjectResource())
v1_api.register(StoryResource())
v1_api.register(TaskResource())
v1_api.register(EpicResource())
v1_api.register(NewsItemResource())
# v1_api.register(CommentResource())
v1_api.register(IterationResource())
v1_api.register(UserResource())
# v1_api.register(ActivityResource())

urlpatterns = v1_api.urls
