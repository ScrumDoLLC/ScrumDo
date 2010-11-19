from datetime import datetime, date
import time
from tagging.fields import TagField
from tagging.models import Tag
from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from groups.base import Group

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
  
  
  
class SiteStats( models.Model ):
  user_count = models.IntegerField();
  project_count = models.IntegerField();
  story_count = models.IntegerField();    
  date = models.DateField( auto_now=True );
  
class PointsLog( models.Model ):
  date = models.DateField( auto_now=True );
  points_claimed = models.IntegerField();
  points_total = models.IntegerField();
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  related_object = generic.GenericForeignKey('content_type', 'object_id')
  def timestamp(self):
    return int((time.mktime(self.date.timetuple()) - time.timezone)*1000)
  
  
class Project(Group):
    
    member_users = models.ManyToManyField(User, through="ProjectMember", verbose_name=_('members'))
    
    # private means only members can see the project
    private = models.BooleanField(_('private'), default=False)
    points_log = generic.GenericRelation( PointsLog )
    current_iterations = None
    default_iteration = None
    # 
    # use_assignee = models.BooleanField( default=False )
    # use_acceptance = models.BooleanField( default=False )
    # use_extra_1 = models.BooleanField( default=False )    
    # use_extra_2 = models.BooleanField( default=False )    
    # use_extra_3 = models.BooleanField( default=False )    
    # extra_1_label = models.CharField(  max_length=25)
    # extra_2_label = models.CharField(  max_length=25)    
    # extra_3_label = models.CharField(  max_length=25)    
      
    def get_default_iteration( self ):
      if self.default_iteration == None:
        iterations = Iteration.objects.filter( project=self, default_iteration=True)
        self.default_iteration = iterations[0]
      return self.default_iteration
      
    def get_current_iterations(self):
      if self.current_iterations == None:
        today = date.today
        self.current_iterations = self.iterations.filter( start_date__lte=today, end_date__gte=today)
      return self.current_iterations
      
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'group_slug': self.slug})
    
    def member_queryset(self):
        return self.member_users.all()
    
    def user_is_member(self, user):
        if ProjectMember.objects.filter(project=self, user=user).count() > 0: # @@@ is there a better way?
            return True
        else:
            return False
    
    def get_url_kwargs(self):
        return {'group_slug': self.slug}


  

class Iteration( models.Model):
  name = models.CharField( "name" , max_length=100)
  detail = models.TextField(_('detail'), blank=True)
  start_date = models.DateField( blank=True, null=True )
  end_date = models.DateField( blank=True, null=True )
  project = models.ForeignKey(Project, related_name="iterations")
  default_iteration = models.BooleanField( default=False )
  points_log = generic.GenericRelation( PointsLog )
  
  
  def __str__(self):
    return self.name


class Story( models.Model ):
  STATUS_TODO = 1;
  STATUS_DOING = 2;
  STATUS_DONE = 3;
  
  POINT_CHOICES = (
      ('?', '?'), 
      ('0', '0'),
      ('1', '1'),
      ('2', '2'),
      ('3', '3'), 
      ('5', '5'), 
      ('8', '8'), 
      ('13', '13'), 
      ('20', '20'), 
      ('40', '40'), 
      ('100', '100'), 
      ('Inf', 'Infinite')  )
  STATUS_CHOICES = (
      (1, "TODO"),
      (2, "In Progress"),
      (3, "Done")   )
  
  rank = models.IntegerField() 
  summary = models.TextField( )
  local_id = models.IntegerField()
  detail = models.TextField( blank=True )
  creator = models.ForeignKey(User, related_name="created_stories", verbose_name=_('creator'))
  created = models.DateTimeField(_('created'), default=datetime.now)
  modified = models.DateTimeField(_('modified'), default=datetime.now) 
  assignee = models.ForeignKey(User, related_name="assigned_stories", verbose_name=_('assignee'), null=True, blank=True)  
  tags = TagField()
  points = models.CharField('points', max_length=3, default="?", choices=POINT_CHOICES ,blank=True)
  iteration = models.ForeignKey( Iteration , related_name="stories")
  project = models.ForeignKey( Project , related_name="stories")
  status = models.IntegerField( max_length=2, choices=STATUS_CHOICES, default=1 )
  # extra_1 = models.TextField( blank=True )
  # extra_2 = models.TextField( blank=True )
  # extra_3 = models.TextField( blank=True )    
  

  
class ProjectMember(models.Model):
    project = models.ForeignKey(Project, related_name="members", verbose_name=_('project'))
    user = models.ForeignKey(User, related_name="projects", verbose_name=_('user'))
    
    away = models.BooleanField(_('away'), default=False)
    away_message = models.CharField(_('away_message'), max_length=500)
    away_since = models.DateTimeField(_('away since'), default=datetime.now)
