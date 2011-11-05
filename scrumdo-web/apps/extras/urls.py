from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('extras.views',
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/hook$', "project_extra_callback", name="projct_extra_callback_url"),
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/enable$', "enable_extra", name="enable_extra_url"),
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/disable$', "disable_extra", name="disable_extra_url"),
    url(r'^(?P<extra_slug>[-\w]*)/(?P<project_slug>[-\w]*)/configure$', "configure_extra", name="configure_extra_url"),    
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/configure/(?P<stage>[-\w]+)$', "configure_extra", name="configure_extra_with_stage"),
    url(r'^(?P<extra_slug>[-\w]+)/(?P<project_slug>[-\w]+)/sync$', "syncronize_extra", name="syncronize_extra_url"),


    url(r'^(?P<project_slug>[-\w]+)$', "project_extras", name="project_extras_url"),
    url(r'^queue/(?P<project_slug>[-\w]+)/import$', "import_stories", name="import_stories_url"),
    url(r'^queue/(?P<project_slug>[-\w]+)/ignore$', "ignore_stories", name="ignore_stories_url"),
    url(r'^queue/(?P<project_slug>[-\w]+)/stories/$', "queued_stories", name="queued_stories_url_no_page", kwargs={"page":1}),        
    url(r'^queue/(?P<project_slug>[-\w]+)/stories/(?P<page>[0-9]+)$', "queued_stories", name="queued_stories_url"),        
    url(r'^queue/(?P<project_slug>[-\w]+)$', "story_queue", name="story_queue_url"),
    
)
