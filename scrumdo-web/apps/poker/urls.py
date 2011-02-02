from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('poker.views',
    url(r'^play/(?P<project_slug>[-\w]+)$', "play", name="play_poker"),
    url(r'^control/(?P<project_slug>[-\w]+)$', "control", name="control_poker"),
)
