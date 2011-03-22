from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from activities.models import Activity,StoryActivity,IterationActivity,DeletedActivity,ActivityLike
from projects.models import ProjectMember, Project
from django.shortcuts import render_to_response, get_object_or_404


# Returns the activities for a given user as an html snippet. 
@login_required
def user_activities(request, page):
  # get all the user's projects
  activities = Activity.getActivitiesForUser(request.user)
  
  paginator = Paginator(activities, 10)
  page_obj = paginator.page(page)

  return render_to_response("activities/activity_list.html", {
    "activities": page_obj.object_list,
    "activities_page":page_obj,
  }, context_instance=RequestContext(request))

@login_required
def like_activity(request, activity_id):
  activity = get_object_or_404(Activity, id=activity_id)
  if not ActivityLike.alreadyLiked(request.user, activity):
    activitylike = ActivityLike(user=request.user,activity=activity)
    activitylike.save()

  return render_to_response("activities/like_activity.html", {
    "likes": activity.numLikes(),
  }, context_instance=RequestContext(request))
