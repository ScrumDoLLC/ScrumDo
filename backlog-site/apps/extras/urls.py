from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('extras.views',
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/hook$', "project_extra_callback", name="projct_extra_callback_url"),
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/enable$', "enable_extra", name="enable_extra_url"),
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/disable$', "disable_extra", name="disable_extra_url"),
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/configure$', "configure_extra", name="configure_extra_url"),
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/sync$', "syncronize_extra", name="syncronize_extra_url"),

    
    url(r'^(?P<project_slug>[-\w]+)$', "project_extras", name="project_extras_url"),    
    url(r'^queue/(?P<project_slug>[-\w]+)/import/(?P<queue_id>[-\w]+)$', "import_story", name="import_story_url"),    
    url(r'^queue/(?P<project_slug>[-\w]+)$', "story_queue", name="story_queue_url"),    
)
