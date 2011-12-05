# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2011 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from projects.models import Project
from organizations.models import Organization, Team

from django.core.exceptions import PermissionDenied

from django.core.cache import cache

CACHE_PERMISSION_SECONDS = 15

def admin_access_or_403(project,user, ignore_active=False):
    if not has_admin_access(project, user, ignore_active=ignore_active):
        raise PermissionDenied()

def read_access_or_403(project,user):
    if not has_read_access(project, user):
        raise PermissionDenied()

def write_access_or_403(project,user):
    if not has_write_access(project, user):
        raise PermissionDenied()

def has_staff_access(organization, user):
    try:
        # if user.is_staff:
        #     return True
        key = cache_key(organization, user, "staff")
        cached_value = cache.get(key)
        if cached_value == None:
            access = organization.teams.filter(access_type="staff",members = user).count() > 0
            cache.set(key, access, CACHE_PERMISSION_SECONDS)
            return access
        else:
            return cached_value
    except:
        return False

def has_admin_access( project, user , ignore_active=False):
    try:
        if not ignore_active:
            if not project.active:
                return False
        key = cache_key(project, user, "admin")
        cached_value = cache.get(key)
        if cached_value == None:
            access = real_has_admin_access(project,user)
            cache.set(key, access, CACHE_PERMISSION_SECONDS)
            return access
        else:
            return cached_value
    except:
        return False

def real_has_admin_access(project, user):
    if user.is_staff:
        return True
    if project.creator == user: 
        return True
    if has_staff_access(project.organization, user):
        return True    
    return Organization.objects.filter( teams__members = user , teams__access_type="admin", teams__projects=project).count() > 0            

def has_write_access( project, user ):
    try:
        if not project.active:
            return False
        key = cache_key(project, user, "write")
        cached_value = cache.get(key)
        if cached_value == None:
            access = real_has_write_access(project,user)
            cache.set(key, access, CACHE_PERMISSION_SECONDS)
            return access
        else:
            return cached_value
    except:
        return False

def real_has_write_access( project, user ):
    if user.is_staff:
        return True
    if has_admin_access( project, user):
        return True
    if project.members.filter(user__id=user.id).count() > 0:
        return True
    return Organization.objects.filter( teams__members = user , teams__access_type="write", teams__projects=project).count() > 0

def has_read_access( project, user ):
    try:
        if not project.private:
        # A public project!
            return True

        if user.is_staff:
            return True

        key = cache_key(project, user, "read")
        cached_value = cache.get(key)
        if cached_value == None:
            access = real_has_read_access(project,user)
            cache.set(key, access, CACHE_PERMISSION_SECONDS)
            return access
        else:
            return cached_value
    except:
        return False


def real_has_read_access(project,user):
    if has_admin_access( project, user):
        return True
    if has_write_access(project, user):
        return True
    return Organization.objects.filter( teams__members = user , teams__projects=project).count() > 0

def cache_key( project, user, acc_type):
    return "acc_%s_%s_%d" % (acc_type, project.slug, user.id)
