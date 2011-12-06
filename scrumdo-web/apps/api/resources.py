from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse

from django.conf import settings

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.validation import Validation, FormValidation

from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse


from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from activities.templatetags.activity_tags import absolute_url
from activities.models import NewsItem
from projects.models import Project,ProjectMember,Story,Iteration,Epic,Task
from organizations.models import Organization, Team
from threadedcomments.models import ThreadedComment

from projects.access import has_read_access, has_write_access

from projects.forms import StoryForm

from auth import ScrumDoAuthentication, ScrumDoAuthorization
from api.models import DeveloperApiKey, UserApiKey
import projects.signals as signals

class UserResource(ModelResource):
    teams = fields.ToManyField('api.resources.TeamResource', 'teams')
    projects = fields.ToManyField('api.resources.ProjectResource', 'user_projects')
    assigned_stories = fields.ToManyField('api.resources.StoryResource', 'assigned_stories', null=True)
    tasks = fields.ToManyField('api.resources.TaskResource','assigned_tasks')

    class Meta:
        queryset = User.objects.all()
        fields = ['username', 'first_name', 'last_name', 'last_login']
        detail_allowed_methods = ['get']
        list_allowed_methods = []
        authentication = ScrumDoAuthentication()

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/self/$" % self._meta.resource_name, self.wrap_view('self_dispatch_detail'), name="api_self_dispatch_detail"),
        ]
    def self_dispatch_detail(self, request, **kwargs):
        self._meta.authentication.is_authenticated(request)
        kwargs['id'] = request.user.id
        return self.dispatch_detail(request, **kwargs)

    def dehydrate(self, bundle):
     # get ALL the users projects (including those discovered through teams), and set the projects to the uri's for those.
        bundle.data['projects'] = map(lambda p: reverse("api_dispatch_detail", kwargs={'resource_name':"project", 'pk': p.id, "api_name": self._meta.api_name}), ProjectMember.getProjectsForUser(User.objects.get(username=bundle.data["username"])))
        return bundle

class OrganizationResource(ModelResource):
    teams = fields.ToManyField('api.resources.TeamResource', 'teams')
    projects = fields.ToManyField('api.resources.ProjectResource', 'projects')

    class Meta:
        queryset = Organization.objects.all()
        list_allowed_methods = ['get', 'post', 'put', 'delete']
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
        list_allowed_methods = ['get', 'post', 'put', 'delete']
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
    tasks = fields.ToManyField('api.resources.TaskResource','tasks')
    epic = fields.ToOneField('api.resources.EpicResource','epic',null=True)
    assignee = fields.ToOneField('api.resources.UserResource','assignee',null=True)

    class Meta:
        queryset = Story.objects.all()
        fields = ['id', 'summary','detail','assignee_id','points', 'iteration_id','project_id', 'status','extra_1','extra_2','extra_3', 'local_id','assignee', 'rank']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = ScrumDoAuthentication()
        authorization = ScrumDoAuthorization(
          lambda u: Q(project__teams__in = u.teams.all())|Q(project__member_users__in = [u]),
          lambda u: Q(project__teams__in = u.teams.filter(Q(access_type="read/write")|Q(access_type="admin")))|Q(project__member_users__in = [u]))
        #     validation = Validation() # FormValidation(form_class=StoryForm)

    def dehydrate(self, bundle):
        # cr = CommentResource()
        # bundle.data['comments'] = map(lambda c: cr.get_resource_uri(c), cr.obj_get_list(content_object__exact=bundle.obj))
        return bundle
        
    def obj_create(self, bundle, request=None, **kwargs):
        res = super(StoryResource, self).obj_create(bundle, request)
        if "pk" in kwargs.keys():
            signals.story_updated.send( sender=request, story=res.obj, user=request.user )
        else:
            signals.story_created.send( sender=request, story=res.obj, user=request.user )
        return res
        
    def obj_delete(self, request=None, **kwargs):
        story = Story.objects.get(pk=kwargs["pk"])
        signals.story_deleted.send( sender=request, story=story, user=request.user )
        super(StoryResource, self).obj_delete(request, pk=kwargs["pk"])
            
    def obj_update(self, bundle, request=None, **kwargs):
        res = super(StoryResource, self).obj_update(bundle, request)
        signals.task_updated.send( sender=request, story=res.obj, user=request.user )
        return res
            
        
        

class TaskResource(ModelResource):
    story = fields.ToOneField('api.resources.StoryResource', 'story')
    assignee = fields.ToOneField('api.resources.UserResource', 'assignee')
    
    class Meta:
        queryset = Task.objects.all()
        fields = ['id', 'summary','complete','order']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = ScrumDoAuthentication()
        authorization = ScrumDoAuthorization(
          lambda u: Q(story__project__teams__in = u.teams.all())|Q(story__project__member_users__in = [u]),
          lambda u: Q(story__project__teams__in = u.teams.filter(Q(access_type="read/write")|Q(access_type="admin")))|Q(story__project__member_users__in = [u]))
        
    def obj_create(self, bundle, request=None, **kwargs):
        res = super(TaskResource, self).obj_create(bundle, request)
        if "pk" in kwargs.keys():
            signals.task_updated.send( sender=request, task=res.obj, user=request.user )
        else:
            signals.task_created.send( sender=request, task=res.obj, user=request.user )
        return res
        
    def obj_delete(self, request=None, **kwargs):
        task = Task.objects.get(pk=kwargs["pk"])
        signals.task_deleted.send( sender=request, task=task, user=request.user )
        super(TaskResource, self).obj_delete(request, pk=kwargs["pk"])
            
    def obj_update(self, bundle, request=None, **kwargs):
        res = super(TaskResource, self).obj_update(bundle, request)
        signals.task_updated.send( sender=request, task=res.obj, user=request.user )
        return res



class EpicResource(ModelResource):
    project = fields.ToOneField('api.resources.ProjectResource', 'project')
    parent = fields.ToOneField('api.resources.EpicResource', 'parent', null=True)
    stories = fields.ToManyField('api.resources.StoryResource','stories')
    
    class Meta:
        queryset = Epic.objects.all()
        fields = ['id', 'summary','detail','points','project_id', 'parent_id', 'status','order','archived', 'local_id']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = ScrumDoAuthentication()
        authorization = ScrumDoAuthorization(
          lambda u: Q(project__teams__in = u.teams.all())|Q(project__member_users__in = [u]),
          lambda u: Q(project__teams__in = u.teams.filter(Q(access_type="read/write")|Q(access_type="admin")))|Q(project__member_users__in = [u]))


class IterationResource(ModelResource):
    stories = fields.ToManyField('api.resources.StoryResource', 'stories')
    project = fields.ToOneField('api.resources.ProjectResource', 'project')

    class Meta:
        queryset = Iteration.objects.all()
        fields = ['id','name', 'start_date','end_date','project_id']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = ScrumDoAuthentication()
        authorization = ScrumDoAuthorization(
          lambda u: Q(project__teams__in = u.teams.all())|Q(project__member_users__in = [u]),
          lambda u: Q(project__teams__in = u.teams.filter(Q(access_type="read/write")|Q(access_type="admin")))|Q(project__member_users__in = [u]))
        
    def obj_create(self, bundle, request=None, **kwargs):
        res = super(IterationResource, self).obj_create(bundle, request)
        if "pk" in kwargs.keys():
            signals.iteration_updated.send( sender=request, iteration=res.obj, user=request.user )
        else:
            signals.iteration_created.send( sender=request, iteration=res.obj, user=request.user )
        return res
        
    def obj_delete(self, request=None, **kwargs):
        iteration = Iteration.objects.get(pk=kwargs["pk"])
        signals.iteration_deleted.send( sender=request, iteration=iteration, user=request.user )
        super(IterationResource, self).obj_delete(request, pk=kwargs["pk"])
            
    

class ProjectResource(ModelResource):
    iterations = fields.ToManyField('api.resources.IterationResource', 'iterations')
    epics = fields.ToManyField('api.resources.EpicResource', 'epics')
    teams = fields.ToManyField('api.resources.TeamResource', 'teams')
    organization = fields.ToOneField(OrganizationResource, 'organization', null=True, full=True)
    member_users = fields.ToManyField('api.resources.UserResource', 'member_users')


    class Meta:
        queryset = Project.objects.all()
        fields = ['name', 'slug', 'creator_id','organization_id','velocity','iterations_left','get_num_stories']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = ScrumDoAuthentication()
        authorization = ScrumDoAuthorization(
           lambda u: Q(teams__in = u.teams.all())|Q(member_users__in = [u]),
           lambda u: Q(teams__in = u.teams.filter(Q(access_type="read/write")|Q(access_type="admin")))|Q(member_users__in = [u]))


class NewsItemResource(ModelResource):
    user = fields.CharField(attribute='user')
    def obj_get_list(self, request=None, **kwargs):
        """ overriding """
        return NewsItem.objects.filter(project__teams__members=request.user)
    def dehydrate_text(self, bundle):        
        return absolute_url(bundle.obj.text)[1:]
    def dehydrate_user(self, bundle):
        return str(bundle.obj.user)
    def dehydrate_icon(self, bundle):
        if "http" == settings.STATIC_URL[:4]:
            return "%simages/%s.png" % (settings.STATIC_URL,bundle.obj.icon)
        else:
            return "%s%simages/%s.png" % (settings.BASE_URL,settings.STATIC_URL,bundle.obj.icon)
    class Meta:
        fields=['created','text','icon','user']
        resource_name = "news"
        queryset = NewsItem.objects.all()
        authentication = ScrumDoAuthentication()
    
# class ActivityResource(ModelResource):
#     def obj_get_list(self, request=None, **kwargs):
#         """ overriding """
#         return Activity.getActivitiesForUser(request.user)
#        
#     line = fields.CharField(readonly=True)
#     #creator = fields.ToOneField('api.resources.UserResource', 'user', full=True)
#     #project = fields.ToOneField('api.resources.ProjectResource', 'project', full=True)
#     #action = fields.ToOneField('api.resources.ActivityActionResource', 'action', full=True)
# 
#     class Meta:
#         queryset = Activity.objects.all()
#         authentication = ScrumDoAuthentication()
#     
#     def dehydrate_line(self, bundle):
#         return bundle.obj.getPrettyActivityString()
