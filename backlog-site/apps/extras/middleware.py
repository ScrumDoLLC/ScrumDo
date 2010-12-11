from django.core.exceptions import MiddlewareNotUsed
from manager import ExtrasManager
from django.conf import settings


# Trick found on http://stackoverflow.com/questions/2781383/where-to-put-django-startup-code to run code on django startup is to have
# a middleware class that raises MiddlewareNotUsed
class ScrumdoExtrasStartupMiddlware(object):
    def __init__(self):
      manager = ExtrasManager( settings.SCRUMDO_EXTRAS )
      raise MiddlewareNotUsed()
        