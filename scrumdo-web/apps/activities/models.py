from django.db import models
import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import  User

class SubjectActivity( models.Model ):	
  news = models.TextField(_('news'))
  user = models.ForeignKey(User,related_name="ActivityByUser", null=True, blank=True)
  action = models.CharField(_("action"), max_length=100)
  object = models.CharField(_("object"), max_length=100)
  story = models.ForeignKey("projects.Story",related_name="ActivityByStory", null=True, blank=True)
  like = models.IntegerField(default=0)
  context = models.CharField(_("context") , max_length=100)
  created = models.DateTimeField(_('created'), default=datetime.datetime.now)

  # Returns all activities for user
  @staticmethod
  def getActivitiesForUser( userl ):
    return SubjectActivity.objects.filter( user = userl ).distinct().order_by('created').reverse()

  @staticmethod
  def activity_handler(sender, **kwargs):
    changeActivity = SubjectActivity(news=kwargs['news'], user=kwargs['user'],action=kwargs['action'],object=kwargs['object'], story=kwargs['story'], context=kwargs['context'])
    changeActivity.save()

  @staticmethod
  def purgeMonthOld():
    today = datetime.date.today()
    mdiff = datetime.timedelta(days=-30)
    date_30days_Agoago = today + mdiff
    SubjectActivity.objects.filter(created__lte=date_30days_Agoago).delete()

    
  # TODO: why is this not getting called
  def is_news_none():
    if news == None:
       print 'News is none'
       return True
    else:
       print 'News is set'
       return False


