from django.db import models
from django.contrib.contenttypes.models import ContentType
import datetime
from itertools import groupby

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import  User

from threadedcomments.models import ThreadedComment

from activities.utils import allinstances, instanceof

from django.core.cache import cache

from scrumdo_model_utils.models import InheritanceCastModel

class ActivityAction(models.Model):
  name = models.TextField(_("action"), max_length=100)

class Activity(InheritanceCastModel):
  user = models.ForeignKey(User,related_name="ActivityByUser", null=True, blank=True)
  action = models.ForeignKey(ActivityAction, related_name="ActivityAction")
  project = models.ForeignKey("projects.Project", related_name="ActivityByProject")
  created = models.DateTimeField(_('created'), default=datetime.datetime.now)

  # Returns all activities for user
  @staticmethod
  def getActivitiesForUser( userl ):
    # try to get from cache first
    activities = cache.get(str(userl.id)+"_activities")
    if activities:
      return activities
    else:
      # is there a better way to do this? importing here is really bad, but can't import at top.
      import projects
      user_projects = projects.models.ProjectMember.getProjectsForUser(userl)
      
      # now get all the stories for the projects a user is interested in
      related_types = {'all':['action','user', 'project'],
                       'storyactivity':['story', 'story__iteration'],
                       'commentactivity':['story'],
                       'pointschangeactivity':['story'],
                       'iterationactivity':['iteration'],
                       }
      activities = Activity.objects.filter(project__in = user_projects).order_by('created').reverse().cast(select_related_types=related_types) #depth=2)

      # this gets a little tricky. we want to get all the subtypes of activity without the expense of creating a query per entry.
      # with django newer than 1.2, this could be provided by django-model-utils InheritanceManager, and one solution from the same library
      # with we partially use, is InheritanceCastModel and InheritanceCastMixin. The problem with the latter is that it does not seem to suppo

      def combine(u, a, it, acts):
        try:
          if a.name == "reordered" and len(acts) > 1:
            story = acts[0].story
            return [IterationActivity(project = story.project, user=u, iteration=story.iteration, created=story.created, action=a, numstories=len(acts))]
          elif allinstances(acts, StoryActivity):
            # if they are the same action about the same story, together, only show the most recent one
            return [list(acts)[0] for (st,s),acts in groupby(acts, lambda act: (act.story_id, act.status))]
          #to add other combinations, simply add elif clauses here
          else:
            return acts
        except:
          return acts

      if len(activities) > 0:
        # this groups the stories by user, action, and iteration if it is not an iteration activity
        groups = groupby(activities, lambda act: (act.user_id, act.action, not instanceof(act, [StoryActivity, CommentActivity, PointsChangeActivity]) or act.story.iteration_id))
        # this goes through the groupings and combines them if necessary
        activities = reduce(lambda x,y: x+y, [combine(u,a,it or stories[0].iteration_id,list(stories)) for (u,a,it),stories in groups])
        cache.set(str(userl.id)+"_activities", activities, 60*10)
        return activities
      else:
        return []
  
  def mergeChildren(self):
    """ this function replaces itself with it's child if the child exists. """
    try:
      return self.storyactivity
    except:
      pass
    try:
      return self.iterationactivity
    except:
      pass
    try:
      return self.deletedactivity
    except:
      pass
    try:
      return self.commentactivity
    except:
      pass
    try:
      return self.pointschangeactivity
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
  # if it is a change status, record what it was changed to
  status = models.CharField("status", max_length=20, null=True)

  def get_absolute_url(self):
    return (self.story.iteration.get_absolute_url() + "#story_" + str(self.story.id))

  @staticmethod
  def activity_handler(sender, **kwargs):
    if "pointschange" in kwargs:
      # this is a pointschanged activity
      return PointsChangeActivity.activity_handler(sender, **kwargs)
    status = None
    if "status" in kwargs:
      status = kwargs['status']
    action = ActivityAction.objects.get(name=kwargs['action'])
    story = sender
    if action.name == "deleted":
      # we want to create a DeletedActivity with the name of the story
      story_name = sender.summary
      storyActivity = DeletedActivity(user=kwargs['user'],action=action,name=story_name, project=kwargs['project'])
    else:
      storyActivity = StoryActivity(user=kwargs['user'],action=action,story=story, project=kwargs['project'], status=status)
    storyActivity.save()


class CommentActivity(Activity):
  story = models.ForeignKey("projects.Story", related_name="StoryCommentActivities")
  comment = models.TextField()

  def get_absolute_url(self):
    return (self.story.iteration.get_absolute_url() + "#story_" + str(self.story.id))

  @staticmethod
  def activity_handler(sender, **kwargs):
    action = ActivityAction.objects.get(name="commented")
    t_comment = kwargs['instance']
    from projects.models import Story
    # check if this is a comment on a story, the only kind we know how to deal with, and that its a new comment.
    if t_comment.content_type.id == ContentType.objects.get_for_model(Story).id and kwargs['created']:
      story = Story.objects.get(id=t_comment.object_id)
      commentActivity = CommentActivity(user=t_comment.user,action=action,story=story,project=story.project,comment=t_comment.comment)
      commentActivity.save()

models.signals.post_save.connect(CommentActivity.activity_handler, sender=ThreadedComment)

class PointsChangeActivity(Activity):
  story = models.ForeignKey("projects.Story", related_name="StoryPointsChangeActivities")
  old = models.CharField('points', max_length=3)
  new = models.CharField('points', max_length=3)

  def get_absolute_url(self):
    return (self.story.iteration.get_absolute_url() + "#story_" + str(self.story.id))

  @staticmethod
  def activity_handler(sender, **kwargs):
    pointsChangeActivity = PointsChangeActivity(user=kwargs['user'],action=ActivityAction.objects.get(name=kwargs['action']),story=kwargs['story'], project=kwargs['project'], old=kwargs['old'], new=kwargs['new'])
    pointsChangeActivity.save()


class IterationActivity(Activity):
  iteration = models.ForeignKey("projects.Iteration", related_name="IterationActivities")
  # for activities that involve manipulation of many stories in a given iteration, note how many
  numstories = models.IntegerField("numstories",null=True)

  def get_absolute_url(self):
    return self.iteration.get_absolute_url()

  @staticmethod
  def activity_handler(sender, **kwargs):
    iteration = sender
    action = ActivityAction.objects.get(name=kwargs['action'])
    if action.name == "deleted":
        return
      # we want to create a DeletedActivity with the name of the iteration
      # 2/15/2010 - this wasn't working...
      # iteration_name = sender.summary
      # iterationActivity = DeletedActivity(user=kwargs['user'],action=action,name=iteration_name, project=kwargs['project'])
    else:
      iterationActivity = IterationActivity(user=kwargs['user'],action=action,iteration=iteration, project=kwargs['project'])
    iterationActivity.save()

class DeletedActivity(Activity):
  """ For an activity about a story that was deleted, archive it's name. The current behavior is that all other activities about the deleted story or iteration are not saved, because since this is not an undoable operation, there doesn't seem to be much value in keeping them. But, we do want to know that the story was deleted, hence this model. """
  name = models.TextField("name")

