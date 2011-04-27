from django.conf.urls.defaults import *

urlpatterns = patterns('developer.views',
  url(r'^$', 'home', name='developer_home'),
  url(r'^apply$', 'apply', name="developer_apply"),
)