from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from activities.models import SubjectActivity
from django.shortcuts import render_to_response, get_object_or_404

# Returns the activities for a given user as an html snippet. 
@login_required
def user_activities(request, page):
  activities = SubjectActivity.getActivitiesForUser(request.user)
  activities.reverse() # why is this not working?
  
  paginator = Paginator(activities, 5)
  page_obj = paginator.page(page)

  return render_to_response("activities/activity_list.html", {
    "activities": page_obj.object_list,
    "activities_page":page_obj,
  }, context_instance=RequestContext(request))

@login_required
def like_activity(request, activity_id):
  activity = get_object_or_404(SubjectActivity, id=activity_id)

  activity.like = activity.like + 1
  activity.save()

  return render_to_response("activities/like_activity.html", {
    "activity": activity,
  }, context_instance=RequestContext(request))
