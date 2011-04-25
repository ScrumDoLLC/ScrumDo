from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.validation import Validation, FormValidation

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from projects.models import Project,ProjectMember,Story,Iteration
from organizations.models import Organization, Team
from threadedcomments.models import ThreadedComment

from projects.access import has_read_access, has_write_access

from projects.forms import StoryForm
 
from auth import ScrumDoAuthentication, ScrumDoAuthorization

class UserResource(ModelResource):
  # teams = fields.ToManyField('api.resources.TeamResource', 'team')
  # projects = fields.ToManyField('api.resources.ProjectResource', 'projects')  
  
  class Meta:
    queryset = User.objects.all()
    fields = ['username', 'first_name', 'last_name', 'last_login']
    allowed_methods = ['get']
    authentication = ScrumDoAuthentication()
    

class OrganizationResource(ModelResource):
  teams = fields.ToManyField('api.resources.TeamResource', 'teams')
  projects = fields.ToManyField('api.resources.ProjectResource', 'projects')
 
  class Meta:
    queryset = Organization.objects.all()
    authentication = ScrumDoAuthentication()
    authorization = ScrumDoAuthorization(
       lambda u: Q(id__in = u.teams.all().values('organization__id').distinct()),
       lambda u: Q(id__in = u.teams.filter(access_type="admin").values('organization__id').distinct()))
    

class TeamResource(ModelResource):
  members = fields.ToManyField('api.resources.UserResource', 'members')
  projects = fields.ToManyField('api.resources.ProjectResource', 'projects')  
  organization = fields.ToOneField('api.resources.OrganizationResource', 'organization')

  class Meta:
    queryset = Team.objects.all()
    authentication = ScrumDoAuthentication()
    authorization = ScrumDoAuthorization(
      lambda u: Q(organization__id__in = u.teams.all().values('organization__id').distinct()),
      lambda u: Q(organization__id__in = u.teams.filter(access_type="admin").values('organization__id').distinct()))
     

# This isn't working right now as I don't know how to get comments only on a specific model (see in StoryResource for what I tried)
# class CommentResource(ModelResource):
#   story = fields.ToOneField('api.resources.StoryResource', 'content_object')
#   class Meta:
#     queryset = ThreadedComment.objects.all()
#     fields = ["comment", "date_modified", "date_submitted"]
#     filtering = {
#                 "content_type": ('exact', ContentType.objects.get_for_model(Story),),
#             }

class StoryResource(ModelResource):
  iteration = fields.ToOneField('api.resources.IterationResource', 'iteration')
  project = fields.ToOneField('api.resources.ProjectResource', 'project')
  creator = fields.ToOneField('api.resources.UserResource', 'creator')
  
  class Meta:
    queryset = Story.objects.all()
    authentication = ScrumDoAuthentication()
    authorization = ScrumDoAuthorization(
      lambda u: Q(project__teams__in = u.teams.all())|Q(project__member_users__in = [u]),
      lambda u: Q(project__teams__in = u.teams.filter(Q(access_type="read/write")|Q(access_type="admin")))|Q(project__member_users__in = [u]))
     #     validation = Validation() # FormValidation(form_class=StoryForm)
    
  def dehydrate(self, bundle):
    # cr = CommentResource()
    # bundle.data['comments'] = map(lambda c: cr.get_resource_uri(c), cr.obj_get_list(content_object__exact=bundle.obj))
    return bundle


class IterationResource(ModelResource):
  stories = fields.ToManyField('api.resources.StoryResource', 'stories')
  project = fields.ToOneField('api.resources.ProjectResource', 'project')

  class Meta:
    queryset = Iteration.objects.all()
    authentication = ScrumDoAuthentication()
    authorization = ScrumDoAuthorization(
      lambda u: Q(project__teams__in = u.teams.all())|Q(project__member_users__in = [u]),
      lambda u: Q(project__teams__in = u.teams.filter(Q(access_type="read/write")|Q(access_type="admin")))|Q(project__member_users__in = [u]))

class ProjectResource(ModelResource):
  iterations = fields.ToManyField('api.resources.IterationResource', 'iterations')
  teams = fields.ToManyField('api.resources.TeamResource', 'teams')
  organization = fields.ToOneField(OrganizationResource, 'organization', null=True)
  members = fields.ToManyField('api.resources.UserResource', 'members')

  class Meta:
    queryset = Project.objects.all()
    fields = ['slug']
    authentication = ScrumDoAuthentication()
    authorization = ScrumDoAuthorization(
       lambda u: Q(teams__in = u.teams.all())|Q(member_users__in = [u]),
       lambda u: Q(teams__in = u.teams.filter(Q(access_type="read/write")|Q(access_type="admin")))|Q(member_users__in = [u]))
       