from django.db import models
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import  User
from django.core.cache import cache
import sys, traceback
from itertools import groupby

from threadedcomments.models import ThreadedComment
from activities.utils import allinstances, instanceof
from scrumdo_model_utils.models import InheritanceCastModel
from scrum_log.models import ScrumLog

from activities.models import *
import projects.signals as signals

import datetime
import traceback
import logging

logger = logging.getLogger(__name__)


mappers = {        
    'rank':lambda val: ("Increased Rank" if val[0] > val[1] else "Decreased Rank"),
    'board_rank':lambda val: ("Increased Rank" if val[0] > val[1] else "Decreased Rank"),
    'summary':lambda val: "Summary: %s -> %s" % val,
    'detail':lambda val: "Detail: %s -> %s" % val,
    'modified': lambda val: None,
    'assignee':lambda val: "Assigned To: %s -> %s" % val,
    'points':lambda val: "Point Value: %s -> %s" % val,
    'iteration':lambda val: "Iteration: %s -> %s" % (val[0].name, val[1].name),
    'project':lambda val: "Project: %s -> %s" % (val[0].name, val[1].name),
    'status':lambda val: "Status: %s -> %s" % (val[0].name, val[1].name),
    'category':lambda val: "Category: %s -> %s" % val,
    'epic':lambda val: "Epic: %s -> %s" % val,
    'extra_1':lambda val: "%s: %s -> %s" % (project.extra_1_label, val[0], val[1]),
    'extra_2':lambda val: "%s: %s -> %s" % (project.extra_2_label, val[0], val[1]),
    'extra_3':lambda val: "%s: %s -> %s" % (project.extra_3_label, val[0], val[1]),   
}

def _translate_diffs(diffs, project):
    if diffs == None:
        return {}
    tdiffs = {}
    for k,v in diffs.iteritems():
        logger.debug("Translate diffs %s %s" % (k,v) )
        if k in mappers:
            newval = mappers[k](v)
            if newval:
                tdiffs[k] = newval
        
    return tdiffs

def _createStoryNewsItem(icon, template, **kwargs):
    try:
        story = kwargs["story"]
        user = kwargs["user"]
        diffs = kwargs.get("diffs",None)
        
        diffs = _translate_diffs(diffs, story.project)
        
        item = NewsItem(user=user, project=story.iteration.project, icon=icon )
        item.text = render_to_string("activities/%s" % template, {'user':user,'story':story, 'diffs':diffs} )
        item.save()
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)    
        
def _createIterationNewsItem(icon, template, **kwargs):
    try:
        iteration = kwargs["iteration"]
        user = kwargs["user"]
        item = NewsItem(user=user, project=iteration.project, icon=icon )
        item.text = render_to_string("activities/%s" % template, {'user':user,'iteration':iteration} )
        item.save()
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)
        
def _createTaskNewsItem(icon, template, **kwargs):
    try:
        task = kwargs["task"]
        user = kwargs["user"]
        diffs = kwargs.get("diffs",None)
        item = NewsItem(user=user, project=task.story.iteration.project, icon=icon )
        item.text = render_to_string("activities/%s" % template, {'user':user,'task':task, 'diffs':diffs} )
        item.save()
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)    


def onStoryCreated(sender, **kwargs):
    _createStoryNewsItem("script_add","new_story.txt", **kwargs)
signals.story_created.connect( onStoryCreated , dispatch_uid="newsfeed_signal_hookup")

def onStoryUpdated(sender, **kwargs):
    _createStoryNewsItem("script_edit","edited_story.txt", **kwargs)
signals.story_updated.connect( onStoryUpdated , dispatch_uid="newsfeed_signal_hookup")

def onStoryStatusChanged(sender, **kwargs):
    _createStoryNewsItem("script_code","status_change_story.txt", **kwargs)     
signals.story_status_changed.connect( onStoryStatusChanged , dispatch_uid="newsfeed_signal_hookup")

def onStoryDeleted(sender, **kwargs):
    _createStoryNewsItem("script_delete","delete_story.txt", **kwargs)         
   
signals.story_deleted.connect( onStoryDeleted , dispatch_uid="newsfeed_signal_hookup")

def onTaskCreated(sender, **kwargs):
    _createTaskNewsItem('drive_add', 'new_task.txt', **kwargs)
signals.task_created.connect( onTaskCreated , dispatch_uid="newsfeed_signal_hookup")

def onTaskStatusChange(sender, **kwargs):
    _createTaskNewsItem('drive_go', 'status_change_task.txt', **kwargs)    
signals.task_status_changed.connect( onTaskStatusChange , dispatch_uid="newsfeed_signal_hookup")

def onTaskUpdated(sender, **kwargs):
    _createTaskNewsItem('drive_edit', 'edited_task.txt', **kwargs)    
signals.task_updated.connect( onTaskUpdated , dispatch_uid="newsfeed_signal_hookup")

def onTaskDeleted(sender, **kwargs):
    _createTaskNewsItem('drive_delete', 'delete_task.txt', **kwargs)    
signals.task_deleted.connect( onTaskDeleted , dispatch_uid="newsfeed_signal_hookup")

def onIterationCreated(sender, **kwargs):
    _createIterationNewsItem("calendar_add", "activities/new_iteration.html", **kwargs)
signals.iteration_created.connect( onIterationCreated , dispatch_uid="newsfeed_signal_hookup")

def onIterationDeleted(sender, **kwargs):
    _createIterationNewsItem("calendar_delete", "activities/delete_iteration.html", **kwargs)
signals.iteration_deleted.connect( onIterationDeleted , dispatch_uid="newsfeed_signal_hookup")



def onScrumLogPosted(sender, instance, signal, *args, **kwargs):
    try:        
        icon = "group"
        if instance.flagged:
            icon = "flag_red"
        item = NewsItem(user=instance.creator, project=instance.project, icon=icon )
        item.text = render_to_string("activities/scrumLog.txt", {'item':instance} )
        item.save()
    except:
        logger.error("Could not create news item")
        traceback.print_exc(file=sys.stdout)
models.signals.post_save.connect(onScrumLogPosted, sender=ScrumLog)


def onCommentPosted(sender, **kwargs):
    t_comment = kwargs['instance']
    from projects.models import Story
    # check if this is a comment on a story, the only kind we know how to deal with, and that its a new comment.
    if t_comment.content_type.id == ContentType.objects.get_for_model(Story).id and kwargs['created']:
        try:
            story = Story.objects.get(id=t_comment.object_id)        
            item = NewsItem(user=t_comment.user, project=story.iteration.project, icon="comment_add" )            
            item.text = render_to_string("activities/comment_on_story.txt", {'story':story,'item':t_comment} )
            item.save()
        except:
            logger.error("Could not create news item")
            traceback.print_exc(file=sys.stdout)
models.signals.post_save.connect(onCommentPosted, sender=ThreadedComment)
