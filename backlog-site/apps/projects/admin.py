from django.contrib import admin
from projects.models import Project, Iteration, SiteStats, Story, StoryTag

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Iteration)
admin.site.register(SiteStats )
admin.site.register(Story )
admin.site.register(StoryTag )