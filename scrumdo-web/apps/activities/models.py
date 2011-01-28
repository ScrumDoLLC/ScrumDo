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

    def combinereorders(reorders):
      # multiple reorders, turn into an iteration activity.
      # this is a change that is not saved to db. it could be, (easily)
      # but it seems to make sense to keep the level of detail available 
      # in case we want to utilize knowledge about all the reorders later
      iteration = reorders[0].story.iteration
      created = reorders[0].created # we take the most recent date
      project = reorders[0].project
      user = reorders[0].user
      action = ActivityAction.objects.get(name="reordered")
      return IterationActivity(project = project, user=user, iteration=iteration, created=created, action=action, numstories=len(reorders))

    # compact multiple reorder activities into one iteration activity
    reorders = []
    newactivities = []
    for a in activities:
      if isinstance(a, StoryActivity) and a.action == ActivityAction.objects.get(name="reordered"):
        if len(reorders) == 0 or (reorders[0].user == a.user and reorders[0].story.iteration == a.story.iteration):
          # this reorder fits our current iteration and user, so append it to the stack
          reorders.append(a)
        else:
          # this reorder does not match, so combine and start again
          if len(reorders) == 1:
            newactivities.extend(reorders)
          else:
            newactivities.append(combinereorders(reorders))
          reorders = [a]
      else:
        if len(reorders) == 0:
          # no reorders to think about
          pass
        elif len(reorders) == 1:
          # if only one reorder happened in a row, then it is its own story
          newactivities.extend(reorders)
          reorders = []
        else:
          newactivities.append(combinereorders(reorders))
          reorders = []
        # regardless of whether there were reorders, stick this non-reorder on the list
        newactivities.append(a)

    if len(reorders) == 1:
      newactivities.extend(reorders)
    elif len(reorders) > 1:
      newactivities.append(combinereorders(reorders))

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

