from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from activities.models import Activity,StoryActivity,IterationActivity,DeletedActivity
from projects.models import ProjectMember, Project
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404


# Returns the activities for a given user as an html snippet. 
@login_required
def user_activities(request, page):
  # get all the user's projects
  activities = Activity.getActivitiesForUser(request.user)
  
  paginator = Paginator(activities, 10)
  try:
    page_obj = paginator.page(page)
  except EmptyPage:
    # someone asked for a page that has no entries
    raise Http404

  return render_to_response("activities/activity_list.html", {
    "activities": page_obj.object_list,
    "activities_page":page_obj,
    }, context_instance=RequestContext(request))

@login_required
def activities_test(request):
  """ this is a version of user_activities that includes closing body tags so django-toolbar works with it """
  r = user_activities(request,1)
  r.write("</body>")
  return r
