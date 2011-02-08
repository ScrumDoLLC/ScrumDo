from django.db import models
from django.contrib.contenttypes.models import ContentType
import datetime
from itertools import groupby

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import  User

from threadedcomments.models import ThreadedComment

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

    # the preceding code has been factored out in api branch, 
    # once that (and this) are merged in, should be replaced with:
    # user_projects = projects.ProjectMember.getProjectsForUser(userl)
      
    # now get all the stories for the projects a user is interested in
    activities = [act.mergeChildren() for act in list(Activity.objects.filter(project__in = user_projects).order_by('created').reverse())]

    def combine(u, a, it, stories):
      if a.name == "reordered" and len(stories) > 1:
        return [IterationActivity(project = it.project, user=u, iteration=it, created=stories[0].created, action=a, numstories=len(stories))]
      #to add other combinations, simply add elif clauses here
      else:
        return stories

    if len(activities) > 0:
      # this groups the stories by user, action, and iteration if it is a story
      groups = groupby(activities, lambda act: (act.user, act.action, not isinstance(act, StoryActivity) or not act.story or act.story.iteration))
      # this goes through the groupings and combines them if necessary
      return reduce(lambda x,y: x+y, [combine(u,a,it or stories[0].iteration,list(stories)) for (u,a,it),stories in groups])
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
      # we want to create a DeletedActivity with the name of the iteration
      iteration_name = sender.summary
      iterationActivity = DeletedActivity(user=kwargs['user'],action=action,name=iteration_name, project=kwargs['project'])
    else:
      iterationActivity = IterationActivity(user=kwargs['user'],action=action,iteration=iteration, project=kwargs['project'])
    iterationActivity.save()

class DeletedActivity(Activity):
  """ For an activity about a story that was deleted, archive it's name. The current behavior is that all other activities about the deleted story or iteration are not saved, because since this is not an undoable operation, there doesn't seem to be much value in keeping them. But, we do want to know that the story was deleted, hence this model. """
  name = models.TextField("name")

