from projects.models import Project
from organizations.models import Organization
from organizations.team_models import Team
from django.core.exceptions import PermissionDenied

from django.core.cache import cache

CACHE_PERMISSION_SECONDS = 30

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
  key = cache_key(project, user, "admin")
  cached_value = cache.get(key)
  if cached_value == None:
    access = Organization.objects.filter( teams__members = user , teams__access_type="admin", teams__projects=project).count() > 0
    cache.set(key, access, CACHE_PERMISSION_SECONDS)
    return access
  else:
    return cached_value
  
  

def has_write_access( project, user ):
  key = cache_key(project, user, "write")
  cached_value = cache.get(key)
  if cached_value == None:
    access = real_has_write_access(project,user)
    cache.set(key, access, CACHE_PERMISSION_SECONDS)
    return access
  else:
    return cached_value
    
def real_has_write_access( project, user ):
    if has_admin_access( project, user):
      return True  
    if project.members.filter(user__id=user.id).count() > 0:
      return True
    return Organization.objects.filter( teams__members = user , teams__access_type="write", teams__projects=project).count() > 0
  
def has_read_access( project, user ):
  if not project.private:
    # A public project!
    return True
    
  key = cache_key(project, user, "read")
  cached_value = cache.get(key)
  if cached_value == None:
    access = real_has_read_access(project,user)
    cache.set(key, access, CACHE_PERMISSION_SECONDS)
    return access
  else:
    return cached_value
    
    
def real_has_read_access(project,user):
  if has_admin_access( project, user):
    return True  
  if has_write_access(project, user):
    return True
  return Organization.objects.filter( teams__members = user , teams__projects=project).count() > 0

def cache_key( project, user, acc_type):
  return "acc_%s_%s_%d" % (acc_type, project.slug, user.id)