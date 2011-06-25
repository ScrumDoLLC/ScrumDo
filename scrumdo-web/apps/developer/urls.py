from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('developer.views',
 url(r'^$', 'home', name='developer_home'),
 url(r'^crossdomain.xml$', direct_to_template, {'template': 'developer/crossdomain.xml'}),
 url(r'^apply$', 'apply', name="developer_apply"),
 url(r'^user_keys$', 'user_keys', name='developer_user_keys'),
 url(r'^(?P<name>\w+)/print', 'docs_print', name="developer_docs_print"),
 url(r'^(?P<name>\w+)/(?P<page>\w+)', 'docs_page', name="developer_docs_page"),
)
