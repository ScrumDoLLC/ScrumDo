# ScrumDo - Agile/Scrum story management web application 
# Copyright (C) 2011 ScrumDo LLC
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers
import datetime

from projects.models import Project, ProjectMember, Iteration, Story
from projects.forms import *
from projects.access import *
import projects.import_export as import_export

@login_required
def iteration(request, group_slug, iteration_id):
   project = get_object_or_404( Project, slug=group_slug )
   read_access_or_403(project,request.user)
   iteration = get_object_or_404( Iteration, id=iteration_id )
   
   if request.method == 'POST': # If the form has been submitted...
     write_access_or_403(project,request.user)
     form = IterationForm( request.POST, instance=iteration)
     if form.is_valid(): # All validation rules pass      
       iteration = form.save(  )
       request.user.message_set.create(message="Iteration Details Saved.")               
   else:
     form = IterationForm( instance=iteration )

   today = datetime.date.today()
   daysLeft = None
   try:
     if iteration.start_date <= today and iteration.end_date >= today:
       daysLeft = (iteration.end_date - today).days
   except:
    pass
   
   add_story_form = StoryForm(project)
   
   return render_to_response("projects/iteration.html", {
       "iteration": iteration,
       "project" : project,
       "iteration_form": form,
       'daysLeft': daysLeft,
       'add_story_form': add_story_form
     }, context_instance=RequestContext(request))



@login_required
def iteration_create(request, group_slug=None):
 project = get_object_or_404(Project, slug=group_slug)  
 write_access_or_403(project,request.user)
 is_member = project.user_is_member(request.user)

 if request.method == 'POST': # If the form has been submitted...
   form = IterationForm(request.POST) # A form bound to the POST data
   if form.is_valid(): 
     iteration = form.save(commit=False)
     iteration.project = project
     iteration.save()     
     request.user.message_set.create(message="Iteration created.") 
     return HttpResponseRedirect( reverse('project_detail', kwargs={'group_slug':project.slug}) ) # Redirect after POST
 else:
   form = IterationForm() # An unbound form

 return render_to_response('projects/new_iteration.html', { 'project':project, 'form': form,  }, context_instance=RequestContext(request))

@login_required
def unlock_iteration(request, group_slug, iteration_id):
  project = get_object_or_404(Project, slug=group_slug)  
  iteration = get_object_or_404(Iteration, id=iteration_id)  
  write_access_or_403(project,request.user)
  if request.method == "POST":
     form = UnlockForm(request.POST)
     if form.is_valid():
       unlock = form.cleaned_data["unlock_iteration"]
       if unlock:
         iteration.locked = False
         iteration.save()
     return HttpResponseRedirect( reverse('iteration', kwargs={'group_slug':project.slug, 'iteration_id':iteration.id}) ) 
  else:
     form = UnlockForm()    
  return render_to_response('projects/unlock_iteration.html', { 'project':project, 'iteration':iteration, 'form': form,  }, context_instance=RequestContext(request))
  
def iteration_import(request, group_slug, iteration_id):
  pass

@login_required
def iteration_export(request, group_slug, iteration_id):
  project = get_object_or_404(Project, slug=group_slug)  
  iteration = get_object_or_404(Iteration, id=iteration_id)  
  write_access_or_403(project,request.user)
  if request.method == "POST":
    form = ExportForm(request.POST)
    form.is_valid()
    format = form.cleaned_data["format"]
    lock = form.cleaned_data["lock_iteration"]
    if lock:
      iteration.locked = True
      iteration.save()
    return import_export.export_iteration(iteration, format)
  else:
    form = ExportForm()
      
  return render_to_response('projects/export_options.html', { 'project':project, 'iteration':iteration, 'form': form,  }, context_instance=RequestContext(request))

