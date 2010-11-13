# -*- coding: utf-8 -*-

"""
We break out workflow elements to enable us to more easily refactor in the
future.
"""

from django.contrib.auth.models import Group

TASK_MANAGER = 'coredev'

def always(task, user):
    return True

def is_assignee(task, user):
    if task.assignee == user:
        return True
    return False

def is_assignee_or_none(task, user):
    # current user is assignee or there is no assignee
    if task.assignee == user or not task.assignee:
        return True
    return False

def is_creator(task, user):
    if task.creator == user:
        return True
    return False

def is_task_manager(task, user):
    if not user or user.is_anonymous():
        return False
    if user.is_superuser:
        return True
    if Group.objects.filter(name__exact=TASK_MANAGER).filter(user=user):
        return True
    return False

def no_assignee(task, user):
    if not task.assignee:
        return True
    return False

def OR(*l):
    # lets you run multiple permissions against a single state transition
    return lambda *args: any(f(*args) for f in l)




STATE_CHOICES = (
    ('1', 'Todo'),
    ('4', 'Doing'), # the assignee is working on it
    ('5', 'Done'), # discussion needed before work can proceed
    ('6', 'Blocked'), # blocked on something or someone (other than discussion)
)




REVERSE_STATE_CHOICES = dict((item[1], item[0]) for item in STATE_CHOICES)

STATE_CHOICES_DICT = dict((item[0], item[1]) for item in STATE_CHOICES)

STATE_ID_LIST = [x[0] for x in STATE_CHOICES]


