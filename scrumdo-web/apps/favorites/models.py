import sys

from datetime import datetime
from projects.models import *
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.db.models.signals import post_save
from django.utils.translation import get_language_from_request, ugettext_lazy as _



class Favorite(models.Model):
    TYPE_CHOICES = ( (0,"Story"),(1,"Project"),(2,"Iteration"),(3,"Epic") )
    user = models.ForeignKey(User, verbose_name=_('user'))
    favorite_type = models.IntegerField( choices=TYPE_CHOICES )
    
    # I really didn't want to use generic fields nor have 4 types of favorites, there's
    # going to be a ton of these and I'll need to index by all of them.
    story     = models.ForeignKey(Story, null=True, blank=True)
    epic      = models.ForeignKey(Epic, null=True, blank=True)
    iteration = models.ForeignKey(Iteration, null=True, blank=True)
    project   = models.ForeignKey(Project, null=True, blank=True)
    
    @staticmethod
    def setFavorite( fav_type, target_id, user, favorite):
        target = Favorite.getTarget(fav_type, target_id)
        existing = Favorite.getTargetFilter(target, Favorite.objects.filter(user=user) )
        if favorite and len(existing) == 0:
            # Favorite does not exist, but we want it            
            f = Favorite(user=user, favorite_type=fav_type)
            f.setTarget(target)
            f.save()
            return
        if (not favorite) and len(existing) > 0:
            # Favorite exists, get rid of it
            for favorite in existing:
                favorite.delete()
            
        
    
    @staticmethod
    def getFavorite( user, target ):
        q = Favorite.objects.filter(user=user)
        q = Favorite.getTargetFilter(target, q)
        items = q.all()
        if len(items) == 0:
            return None
        if len(items) > 1:
            logger.error("Found multiple favorites for %s / %s" % (user, target))
        return items[0]

    @staticmethod
    def getTarget( fav_type, target_id ):
        if fav_type == 0:
            return Story.objects.get(id=target_id)
        if fav_type == 3:
            return Epic.objects.get(id=target_id)
        if fav_type == 2:
            return Iteration.objects.get(id=target_id)
        if fav_type == 1:
            return Project.objects.get(id=target_id)
    
    @staticmethod
    def getTargetType( target ):
        if isinstance(target, Story):
            return 0
        if isinstance(target, Epic):
            return 3
        if isinstance(target, Iteration):
            return 2
        if isinstance(target, Project):
            return 1

    @staticmethod
    def getTargetFilter(target, q):
        if isinstance(target, Story):
            return q.filter(story=target)
        if isinstance(target, Epic):
            return q.filter(epic=target)
        if isinstance(target, Iteration):
            return q.filter(iteration=target)
        if isinstance(target, Project):
            return q.filter(project=target)
        
    def setTarget(self, target):
        if isinstance(target, Story):
            self.story = target
        if isinstance(target, Epic):
            self.epic = target
        if isinstance(target, Iteration):
            self.iteration = target
        if isinstance(target, Project):
            self.project = target
