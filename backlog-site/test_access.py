#!/usr/bin/env python
import sys
from datetime import date, timedelta

from os.path import abspath, dirname, join

try:
    import pinax
except ImportError:
    sys.stderr.write("Error: Can't import Pinax. Make sure you are in a virtual environment that has Pinax installed or create one with pinax-boot.py.\n")
    sys.exit(1)

from django.conf import settings
from django.core.management import setup_environ, execute_from_command_line

try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))


from projects.access import *
from projects.models import *
from organizations.models import *
from organizations.team_models import *
from django.contrib.auth.models import User

for project in Project.objects.all():
  print "Project %s " % project.slug
  for user in User.objects.all():
    if has_admin_access(project, user):
      print "  Admin:  %s" % user.username
    if has_write_access(project, user):
      print "  Write:  %s" % user.username
    if has_read_access( project, user):
      print "  Read:  %s" % user.username
  