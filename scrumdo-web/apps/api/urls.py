from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from api.handlers import ProjectHandler

auth = HttpBasicAuthentication(realm="ScrumDo Test Auth")
ad = { 'authentication': auth }

project_handler = Resource(ProjectHandler, **ad)

urlpatterns = patterns('',
   url(r'^project/(?P<slug>[^/]+)/', project_handler),
   url(r'^projects/', project_handler),
)
