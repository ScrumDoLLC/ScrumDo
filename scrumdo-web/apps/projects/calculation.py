from datetime import date, timedelta
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError

from projects.limits import on_demand_velocity

import logging

logger = logging.getLogger(__name__)

def onDemandCalculateVelocity( project ):
    if not on_demand_velocity.increaseAllowed(project=project):
        return
    calculateProject( project )

def calculatePoints( stories ):
    points_total = 0;
    points_claimed = 0;
    for story in stories:
        try:
            story_points = story.points_value()
            points_total += story_points
            # print "%d %f" % ( story.id,story_points)
            if( story.status == Story.STATUS_DONE):
                points_claimed += story_points
        except ValueError:            
            pass # probably ? or infinity

    #print (points_total, points_claimed)
    return (points_total, points_claimed)

def calculateProjectVelocity( project, total_project_points ):
    today = date.today()
    # Loop through all completed iterations and gather info
    iteration_points = []
    for iteration in project.iterations.filter( end_date__lte=today):
        if not iteration.default_iteration and iteration.include_in_velocity:
            points = 0
            for story in iteration.stories.all():
                if story.status == Story.STATUS_DONE:
                    try:
                        points += story.points_value()
                    except ValueError:
                        pass # probably ? or infinity
            iteration_points.append( points )

    velocity = 0
    if project.velocity_type == project.VELOCITY_TYPE_AVERAGE:
        velocity = calculateAverage( iteration_points )
    elif project.velocity_type == project.VELOCITY_TYPE_AVERAGE_5:
        velocity = calculateAverageLastN( iteration_points , 5)
    elif project.velocity_type == project.VELOCITY_TYPE_AVERAGE_3:
        velocity = calculateAverageLastN( iteration_points , 3)
    else:
        velocity = calculateMedian( iteration_points )

    project.velocity = velocity
    if project.velocity > 0:
        project.iterations_left = int( total_project_points / project.velocity)

    project.save();


def calculateMedian( iteration_points ):
    if len(iteration_points) == 0:
        return 0
    sorted_list = sorted( iteration_points )
    return sorted_list[ int(len( iteration_points ) / 2 ) ]



def calculateAverageLastN( iteration_points , n):
    if len(iteration_points) <= n:
        return calculateAverage( iteration_points )
    total = sum( iteration_points[-n:] )
    return total / n



def calculateAverage( iteration_points ):
    if len( iteration_points ) == 0:
        return 0
    total = sum( iteration_points )
    #print "%d / %d" % (total, len(iteration_points))
    return total / len( iteration_points )


def logPoints( related_object, points_claimed, points_total ):
    today = date.today()
    # logger.info("%s %d %f" % (related_object, points_claimed, points_total) )
    try:
        log = related_object.points_log.get( date=today )
        log.points_claimed=points_claimed
        log.points_total=points_total
        log.save()
        # logger.debug("logPoints found a previous record.")
    except PointsLog.DoesNotExist:
        log = PointsLog( points_claimed=points_claimed, points_total=points_total, related_object=related_object)
        log.save()
        # logger.debug("logPoints created a new record.")

def calculateProject( project ):
    stories = project.stories.all();
    points = calculatePoints( stories )
    total_project_points = points[0]
    
    today = date.today()
    
    logPoints(project, points[1], points[0])
    # log = PointsLog( points_claimed=points[1], points_total=points[0], related_object=project)
    # log.save();
    
    
    yesterday = today - timedelta( days=1 )
    tomorrow = today +  timedelta( days=1 )
    points_total = 0

    calculateProjectVelocity( project , total_project_points)

    for iteration in project.iterations.filter( start_date__lte=tomorrow, end_date__gte=yesterday):
        if( iteration != project.get_default_iteration() ):
            points = calculatePoints( iteration.stories.all() );
            if points[0] > 0:  # only logging active iterations with stuff in them
                logPoints(iteration, points[1], points[0])
                # log = PointsLog( points_claimed=points[1], points_total=points[0], related_object=iteration)
                # log.save();
