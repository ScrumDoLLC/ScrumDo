#!/usr/bin/env python
import sys

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

from apps.projects.models import Project, Iteration, Story, PointsLog


def calculatePoints( stories ):
  points_total = 0;
  points_claimed = 0;
  for story in stories:
    try:
      story_points = int(story.points);
      points_total += story_points
      if( story.status == Story.STATUS_DONE):
        points_claimed += story_points
    except ValueError:
      pass # probably ? or infinity
  return (points_total, points_claimed)


def calculateProject( project ):
  stories = project.stories.all();
  points = calculatePoints( stories )
  log = PointsLog( points_claimed=points[1], points_total=points[0], related_object=project)
  print "%d / %d / %s " % (log.points_total, log.points_claimed, project.name );
  log.save();
  for iteration in project.iterations.all():
    if( iteration != project.get_default_iteration() ):    
      points = calculatePoints( iteration.stories.all() );
      log = PointsLog( points_claimed=points[1], points_total=points[0], related_object=iteration)
      print ">  %d / %d / %s " % (log.points_total, log.points_claimed, iteration.name );
      log.save();

def main():
  projects = Project.objects.all()
  for project in projects:
    calculateProject( project )


if __name__ == "__main__":
    main()
