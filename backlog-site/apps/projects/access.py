from projects.models import Project
from organizations.models import Organization
from organizations.team_models import Team
from django.core.exceptions import PermissionDenied

def admin_access_or_403(project,user):
  if not has_admin_access(project, user):
    raise PermissionDenied()

def read_access_or_403(project,user):
  if not has_read_access(project, user):
    raise PermissionDenied()

def write_access_or_403(project,user):
  if not has_write_access(project, user):
    raise PermissionDenied()

def has_admin_access( project, user ):
  if project.creator == user: return True
  return Organization.objects.filter( teams__members = user , teams__access_type="admin", teams__projects=project).count() > 0
  
def has_write_access( project, user ):
  if has_admin_access( project, user):
    return True  
  if project.members.filter(user__id=user.id).count() > 0:
    return True
  return Organization.objects.filter( teams__members = user , teams__access_type="write", teams__projects=project).count() > 0
  
def has_read_access( project, user ):
  if has_admin_access( project, user):
    return True  
  if has_write_access(project, user):
    return True
  return Organization.objects.filter( teams__members = user , teams__projects=project).count() > 0
