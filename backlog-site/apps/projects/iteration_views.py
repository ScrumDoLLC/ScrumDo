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
@login_required
def iteration(request, group_slug, iteration_id):
   project = get_object_or_404( Project, slug=group_slug )
   iteration = get_object_or_404( Iteration, id=iteration_id )

   
   if request.method == 'POST': # If the form has been submitted...
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
 is_member = project.user_is_member(request.user)

 if not is_member:
   return HttpResponseForbidden()

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



