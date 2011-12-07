from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('scrum_log.views',
    url(r'^(?P<project_slug>[-\w]+)/add_scrum_log_ajax$', "add_scrum_log_ajax", name="add_scrum_log_ajax"),
    url(r'^(?P<project_slug>[-\w]+)/entries/(?P<page>[0-9]+)$', "entries", name="entries"),
    url(r'^(?P<id>[0-9]+)/delete$', "delete_log_entry", name="delete_log_entry"),
)
