from piston.handler import BaseHandler
from piston.utils import rc
from projects.models import Project,ProjectMember,Story
from activities.models import SubjectActivity

class ProjectHandler(BaseHandler):
   allowed_methods = ('GET',)
   model = Project  

   def read(self, request, slug=None):
       """
       returns a single project if group_slug is specified,
       else all projects authenticated user has access to.
       """
       if slug:
           p = Project.objects.get(slug=slug)
           if p.hasReadAccess(request.user):
               return p
           else:
               return rc.FORBIDDEN
       else:
           return [pm.project for pm in ProjectMember.objects.filter(user=request.user)]
