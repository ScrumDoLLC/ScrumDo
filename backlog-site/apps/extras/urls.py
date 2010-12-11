from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('extras.views',
    url(r'^(?P<extra_slug>[-\w]+)/project/(?P<project_slug>[-\w]+)/hook$', "project_extra_callback", name="projct_extra_callback_url"),
    url(r'^(?P<extra_slug>[-\w]+)/project/(?P<project_slug>[-\w]+)$', "project_extra_options", name="projct_extra_options_url"),
    url(r'^/project/(?P<project_slug>[-\w]+)$', "project_extras", name="project_extras_url"),    
)
