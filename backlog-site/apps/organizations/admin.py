from django.contrib import admin
from organizations.models import Organization
from organizations.team_models import Team

admin.site.register(Organization)
admin.site.register(Team )