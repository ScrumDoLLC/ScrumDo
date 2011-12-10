from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from projects.models import ProjectMember, Project
from organizations.models import Organization
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from activities.models import ProjectEmailSubscription

import logging

logger = logging.getLogger(__name__)

@login_required
def activities_test(request):
    """ this is a version of user_activities that includes closing body tags so django-toolbar works with it """
    r = user_activities(request,1)
    r.write("</body>")
    return r


@login_required
def activity_subscriptions(request):
    organizations = Organization.getOrganizationsForUser(request.user)

    subscription_objs =  ProjectEmailSubscription.objects.filter(user=request.user)
    if request.method == "POST":
        subscriptions = request.POST.getlist('subscriptions')
        subscriptions = [int(sub) for sub in subscriptions]
        # remove any unchecked...
        for old_sub in subscription_objs:
            if not old_sub.project.id in subscriptions:
                old_sub.delete()
        # add any new ones
        for new_sub in subscriptions:
            if len([ sub for sub in subscription_objs if sub.project.id==new_sub ]) == 0 :
                project = Project.objects.get(id=new_sub)
                s = ProjectEmailSubscription( user=request.user, project=project)
                s.save()
    else:
        subscriptions = [ sub.project.id for sub in subscription_objs ]

    return render_to_response("activities/email_subscription.html", { "organizations":organizations, "subscriptions":subscriptions
      }, context_instance=RequestContext(request))
