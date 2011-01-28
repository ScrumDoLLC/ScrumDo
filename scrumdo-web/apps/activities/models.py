from django.db import models
import datetime
from itertools import groupby

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
      
    # now get all the stories for the projects a user is interested in
    activities = [act.mergeChildren() for act in list(Activity.objects.filter(project__in = user_projects).order_by('created').reverse())]

    def combine(u, a, it, stories):
      if it and a.name == "reordered" and len(stories) > 1:
        return [IterationActivity(project = it.project, user=u, iteration=it, created=stories[0].created, action=a, numstories=len(stories))]
      #to add other combinations, simply add elif clauses here
      else:
        return stories

    # this groups the stories by user, action, and iteration if it is a story
    groups = groupby(activities, lambda act: (act.user, act.action, not isinstance(act, StoryActivity) or act.story.iteration))
    # this goes through the groupings and combines them if necessary
    newactivities = reduce(lambda x,y: x+y, [combine(u,a,it,list(stories)) for (u,a,it),stories in groups])

    return newactivities

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
  # for activities that involve manipulation of many stories in a given iteration, note how many
  numstories = models.IntegerField(null=True)

  def get_absolute_url(self):
    return self.iteration.get_absolute_url()

  @staticmethod
  def activity_handler(sender, **kwargs):
    iterationActivity = IterationActivity(user=kwargs['user'],action=ActivityAction.objects.get(name=kwargs['action']),iteration=sender, project=kwargs['project'])
    iterationActivity.save()

