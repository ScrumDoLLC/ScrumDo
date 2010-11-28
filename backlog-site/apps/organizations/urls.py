from django.conf.urls.defaults import *

from organizations.models import Organization
from organizations.team_models import Team

# from groups.bridge import ContentBridge
# 
# 
# bridge = ContentBridge(Project, 'projects')

urlpatterns = patterns('organizations.views',
    url(r'^debug/$', "team_debug"),
    url(r'^create/$', 'organization_create', name="organization_create"),
    url(r'^list/$', 'your_organizations', name="your_organizations"),    
    url(r'^(?P<organization_slug>[-\w]+)/$', 'organization', name="organization_detail")        
)


urlpatterns += patterns('organizations.team_views',
   url(r'^(?P<organization_slug>[-\w]+)/team/create$', 'team_create', name="team_create"),
   url(r'^(?P<organization_slug>[-\w]+)/team/(?P<team_id>[-\w]+)$', 'team', name="team_detail"),

)