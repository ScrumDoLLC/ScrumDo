from django.db import models
from django.db.models import Q

class ForumManager(models.Manager):
    def for_groups(self, groups):
        if groups:
            public = Q(groups__isnull=True)
            user_groups = Q(groups__in=groups)
            return self.filter(public|user_groups).distinct()
        return self.filter(groups__isnull=True)
    
    def has_access(self, forum, groups):
        return forum in self.for_groups(groups)
