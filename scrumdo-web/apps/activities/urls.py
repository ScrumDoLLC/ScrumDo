from django.conf.urls.defaults import *

urlpatterns = patterns('activities.views',
url(r'^user/(?P<page>\w+)$', 'user_activities', name="user_activities"),
)
