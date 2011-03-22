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

from projects.calculation import onDemandCalculateVelocity

from projects.models import Project, ProjectMember, Iteration, Story
from projects.forms import *
from projects.access import *
import projects.import_export as import_export

from activities.models import ActivityAction
from story_views import handleAddStory

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

    add_story_form = handleAddStory(request, project)

    return render_to_response("projects/iteration.html", {
        "iteration": iteration,
        "iterationinfo": True,
        "project" : project,
        "iteration_form": form,
        'daysLeft': daysLeft,
        'add_story_form': add_story_form,
        "current_view":"iteration_page"
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
            action = "created"
            iteration.activity_signal.send(sender=iteration, user=request.user, action=action, project=project)
            request.user.message_set.create(message="Iteration created.")
            return HttpResponseRedirect( reverse('project_detail', kwargs={'group_slug':project.slug}) ) # Redirect after POST

    else:
        form = IterationForm() # An unbound form

    return render_to_response('projects/new_iteration.html', { 'project':project, 'form': form,  }, context_instance=RequestContext(request))


# Deletes an iteration.  No further confirmation, but it will only do it if the iteration
# is empty. Also, some confirmation client-side.
@login_required
def delete_iteration( request, group_slug, iteration_id ):
    iteration = get_object_or_404( Iteration, id=iteration_id )

    if iteration.default_iteration:
        request.user.message_set.create(message="You can not delete the default iteration.")
        HttpResponseRedirect( reverse('iteration', kwargs={'group_slug':iteration.project.slug, 'iteration_id':iteration.id }) ) #redirect to same iteration+display msg., as delete failed

    if request.method == "POST":
        write_access_or_403(iteration.project,request.user)
        # dont think this signal exists.
        # signals.iteration_deleted.send( sender=request, iteration=iteration, user=request.user )
        stories = Story.objects.filter(iteration = iteration)
        if not stories:
            iteration.delete()
            iteration.activity_signal.send(sender=Iteration, news=request.user.username + " deleted\"" +iteration.name + "\" in project\"" +iteration.project.name, user=request.user,action="deleted" ,object=iteration.name, story = None, context=iteration.project.slug)
            request.user.message_set.create(message="Iteration deleted.")
            return HttpResponseRedirect( reverse('project_detail', kwargs={'group_slug':iteration.project.slug}) ) # Redirect after POST, to the only logical place
        else:
            request.user.message_set.create(message="Iteration not empty, could not be deleted.")
    return HttpResponseRedirect( reverse('iteration', kwargs={'group_slug':iteration.project.slug, 'iteration_id':iteration.id }) ) #redirect to same iteration+display msg., as delete failed


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



@login_required
def iteration_import(request, group_slug, iteration_id):
    project = get_object_or_404(Project, slug=group_slug)
    iteration = get_object_or_404(Iteration, id=iteration_id)

    if iteration.locked:
        form_class = IterationImportFormWithUnlock
    else:
        form_class = IterationImportForm

    write_access_or_403(project,request.user)
    if request.method == "POST":
        form = form_class(request.POST)
        import_file = request.FILES.get("import_file",None)
        if form.is_valid() and import_file != None:
            unlock = form.cleaned_data.get("unlock_iteration",False)
            if unlock:
                iteration.locked = False
                iteration.save()
            status = import_export.importIteration(iteration, import_file, request.user )
            onDemandCalculateVelocity( project )
        return HttpResponseRedirect( reverse('iteration', kwargs={'group_slug':project.slug, 'iteration_id':iteration.id}) )
    else:
        form = form_class(  )

    return render_to_response('projects/import_options.html', { 'project':project, 'iteration':iteration, 'form': form,  }, context_instance=RequestContext(request))

@login_required
def iteration_report(request, group_slug, iteration_id):
    project = get_object_or_404(Project, slug=group_slug)
    iteration = get_object_or_404(Iteration, id=iteration_id)
    read_access_or_403(project,request.user)
    return render_to_response('projects/iteration_report.html', { 'project':project, 'iteration':iteration  }, context_instance=RequestContext(request))

@login_required
def iteration_export(request, group_slug, iteration_id):
    project = get_object_or_404(Project, slug=group_slug)
    iteration = get_object_or_404(Iteration, id=iteration_id)
    write_access_or_403(project,request.user)
    if request.method == "POST":
        form = ExportForm(request.POST)
        if form.is_valid():
            format = form.cleaned_data["format"]
            lock = form.cleaned_data["lock_iteration"]
            if lock:
                iteration.locked = True
                iteration.save()
            return import_export.exportIteration(iteration, format)
    else:
        form = ExportForm()

    return render_to_response('projects/export_options.html', { 'project':project, 'iteration':iteration, 'form': form,  }, context_instance=RequestContext(request))
