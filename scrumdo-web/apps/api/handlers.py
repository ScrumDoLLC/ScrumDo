from piston.handler import BaseHandler
from piston.utils import rc
from projects.models import Project,ProjectMember,Story,Iteration
from activities.models import Activity, StoryActivity, IterationActivity, DeletedActivity

class ProjectHandler(BaseHandler):
   allowed_methods = ('GET',)
   model = Project  

   def read(self, request, slug=None, user=False, org=False):
       """
       returns a single project if slug is specified,
       the users projects if user is True, an organization's
       projects if org_slug is specified
       else all projects authenticated user has access to.
       """
       if slug and (not org):
          p = Project.objects.get(slug=slug)
          if p.hasReadAccess(request.user):
             return p
          else:
             return rc.FORBIDDEN
       elif user:
          return Project.objects.filter(creator=request.user)
       elif org:
          return Project.objects.filter(organization__slug = slug)
       else:
          return ProjectMember.getProjectsForUser(request.user)

class IterationHandler(BaseHandler):
   allowed_methods = ('GET',)
   model = Iteration  

   def read(self, request, slug):
      """ given a project slug, returns all the iterations 
      associated with that project """
      return Iteration.objects.filter(project__slug = slug)


class StoryHandler(BaseHandler):
   allowed_methods = ('GET', 'POST', 'DELETE')
   model = Story

   def read(self, request, slug, iteration_id):
      """ given a project slug and iteration id, return all stories 
      associated with that iteration """
      return Story.objects.filter(project__slug = slug, iteration__id = iteration_id)

   def create(self, request, slug, story_id=None):
      if story_id:
         # this is a comment on a story
         pass
      else:
         # creating a new story
         pass

   def delete(self, request, slug, story_id):
        story = Story.objects.get(id=story_id)
        if story.iteration.locked or not story.project.hasWriteAccess(request.user):
           return rc.FORBIDDEN # returns HTTP 401
        else:
           story.delete()
           return rc.DELETED


class NewsfeedHandler(BaseHandler):
   allowed_methods = ('GET',)
   model = Activity  

   def read(self, request, num=20):
      """ returns a given user's newsfeed stories (optional param specifying how many """
      return Activity.getActivitiesForUser(request.user)[:int(num)]

