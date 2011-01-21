from django.conf.urls.defaults import *

urlpatterns = patterns('tutorial.views',
    url(r'^(?P<page>\d+)', 'tutorial', name="tutorial_page"),
)
