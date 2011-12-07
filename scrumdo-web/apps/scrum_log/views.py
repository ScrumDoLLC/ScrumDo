from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers

from projects.models import Project
from projects.access import *
from models import ScrumLog

import json
import datetime
import logging

logger = logging.getLogger(__name__)

@login_required
def delete_log_entry(request, id):
    entry = get_object_or_404( ScrumLog, id=id )
    write_access_or_403(entry.project, request.user )
    if (entry.creator != request.user) and not has_admin_access(entry.project, request.user):
        return HttpResponse("FAILED")
    entry.delete()
    return HttpResponse("OK")
    
@login_required
def entries(request, project_slug, page):
    project = get_object_or_404( Project, slug=project_slug )
    read_access_or_403(project, request.user )
    items = project.log_items.all().order_by("-date")
    logger.debug(items.count())
    pages = Paginator(items, 20)
    
    if items.count() == 0:
        return render_to_response("scrum_log/empty_scrum_log.html", 
                                  {},
                                  context_instance=RequestContext(request))
        
    
    try:
        page_items = pages.page(page)
    except:
        return HttpResponse("")        
    
    return render_to_response("scrum_log/scrum_log_entries.html", 
                              {
                                "entries":page_items.object_list,
                                "project":project,
                                "page":page
                              },
                              context_instance=RequestContext(request))

@login_required
def add_scrum_log_ajax(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    write_access_or_403(project, request.user )
    message = request.POST.get("message")
    if message==None or len(message) == 0:
        return HttpResponse("FAILED")
    message_type = 1 if (request.POST.get("group") == "on" ) else 0
    flagged = request.POST.get("flagged") == "on"
    logger.debug(request.POST.get("flagged"))
    log = ScrumLog(creator=request.user, 
                   project=project,
                   message=message,
                   message_type=message_type,
                   flagged=flagged )
    log.save()
    return HttpResponse("OK")