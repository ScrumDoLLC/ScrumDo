from django.db import models
import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import  User

class ActivityAction(models.Model):
  name = models.TextField(_("action"), max_length=100)

class ActivityLike(models.Model):
  user = models.ForeignKey(User)
  activity = models.ForeignKey("Activity")

  @staticmethod
  def alreadyLiked(user, activity):
    try:
      ActivityLike.objects.get(user=user, activity=activity)
      return True
    except:
      return False

class Activity(models.Model):
  user = models.ForeignKey(User,related_name="ActivityByUser", null=True, blank=True)
  action = models.ForeignKey(ActivityAction, related_name="ActivityAction")
  project = models.ForeignKey("projects.Project", related_name="ActivityByProject")
  created = models.DateTimeField(_('created'), default=datetime.datetime.now)

  def numLikes(self):
    return ActivityLike.objects.filter(activity=self).count()

  # Returns all activities for user
  @staticmethod
  def getActivitiesForUser( userl ):
    # is there a better way to do this? importing here is really bad, but can't import at top.
    import projects, organizations
    user_projects = [pm.project for pm in projects.models.ProjectMember.objects.filter(user=userl).select_related()]
    team_projects = [team.projects.all() for team in organizations.team_models.Team.objects.filter(members=userl)]
    for project_list in team_projects:
      user_projects = user_projects + list(project_list)

#    activities = []
#    for project in user_projects:
    activities = [act.mergeChildren() for act in list(Activity.objects.filter(project__in = user_projects).order_by('created').reverse())]
    return activities

  def mergeChildren(self):
    """ this function replaces itself with it's child if the child exists. """
    try:
      self.storyactivity
      return self.storyactivity
    except:
      pass
    try:
      self.iterationactivity
      return self.iterationactivity
    except:
      pass
    return self

  @staticmethod
  def purgeMonthOld():
    today = datetime.date.today()
    mdiff = datetime.timedelta(days=-30)
    date_30days_Agoago = today + mdiff
    Activity.objects.filter(created__lte=date_30days_Agoago).delete()


class StoryActivity(Activity):
  story = models.ForeignKey("projects.Story", related_name="StoryActivities")
  status = models.CharField("status", max_length=20, null=True)

  def get_absolute_url(self):
    return (self.story.iteration.get_absolute_url() + "#story_" + str(self.story.id))

  @staticmethod
  def activity_handler(sender, **kwargs):
    status = None
    if "status" in kwargs:
      status = kwargs['status']
    storyActivity = StoryActivity(user=kwargs['user'],action=ActivityAction.objects.get(name=kwargs['action']),story=sender, project=kwargs['project'], status=status)
    storyActivity.save()


class IterationActivity(Activity):
  iteration = models.ForeignKey("projects.Iteration", related_name="IterationActivities")

  def get_absolute_url(self):
    return self.iteration.get_absolute_url()

  @staticmethod
  def activity_handler(sender, **kwargs):
    iterationActivity = IterationActivity(user=kwargs['user'],action=ActivityAction.objects.get(name=kwargs['action']),iteration=sender, project=kwargs['project'])
    iterationActivity.save()

