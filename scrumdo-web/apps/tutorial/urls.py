from django.conf.urls.defaults import *

urlpatterns = patterns('tutorial.views',
    url(r'^(?P<name>\w+)/print', 'tutorial_print', name="tutorial_print"),
    url(r'^(?P<name>\w+)/(?P<page>\w+)', 'tutorial', name="tutorial_page"),
)
