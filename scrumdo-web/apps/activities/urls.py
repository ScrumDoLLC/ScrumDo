from django.conf.urls.defaults import *

urlpatterns = patterns('activities.views',
url(r'^subscription/$', 'activity_subscriptions', name="activity_subscriptions"),
url(r'^test/$', 'activities_test', name="activities_test"),
)
