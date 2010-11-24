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
  total_project_points = points[0]
  log = PointsLog( points_claimed=points[1], points_total=points[0], related_object=project)
  
  log.save();
  today = date.today()
  yesterday = today - timedelta( days=1 )
  tomorrow = today +  timedelta( days=1 )  
  points_total = 0
  iterations_total = 0  
  for iteration in project.iterations.filter( end_date__lte=today):
    if not iteration.default_iteration and iteration.include_in_velocity:
      iterations_total += 1
      for story in iteration.stories.all():
        if story.status == Story.STATUS_DONE:
          try:
            points_total += int(story.points)
          except ValueError:
            pass # probably ? or infinity
  
  if iterations_total > 0:
    project.velocity = int(points_total / iterations_total)
    if project.velocity > 0:
      project.iterations_left = int( total_project_points / project.velocity)
  else:
    project.velocity = 0
    project.iterations_left = None;
  
  project.save();
      
  print "%d / %d / %d / %s " % (project.velocity, log.points_total, log.points_claimed, project.name );
  
  for iteration in project.iterations.filter( start_date__lte=yesterday, end_date__gte=tomorrow):
    if( iteration != project.get_default_iteration() ):    
      points = calculatePoints( iteration.stories.all() );
      if points[0] > 0:  # only logging active iterations with stuff in them
        log = PointsLog( points_claimed=points[1], points_total=points[0], related_object=iteration)
        print ">  %d / %d / %s " % (log.points_total, log.points_claimed, iteration.name );
        log.save();

def main():
  projects = Project.objects.all()
  for project in projects:
    calculateProject( project )


if __name__ == "__main__":
    main()
