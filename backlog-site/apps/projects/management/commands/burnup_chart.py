#!/usr/bin/env python
from datetime import date, timedelta
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError

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
  
  for iteration in project.iterations.filter( start_date__lte=tomorrow, end_date__gte=yesterday):
    if( iteration != project.get_default_iteration() ):    
      points = calculatePoints( iteration.stories.all() );
      if points[0] > 0:  # only logging active iterations with stuff in them
        log = PointsLog( points_claimed=points[1], points_total=points[0], related_object=iteration)
        print ">  %d / %d / %s " % (log.points_total, log.points_claimed, iteration.name );
        log.save();


        


class Command(BaseCommand):
  def handle(self, *args, **options):
    projects = Project.objects.all()
    for project in projects:
      calculateProject( project )

