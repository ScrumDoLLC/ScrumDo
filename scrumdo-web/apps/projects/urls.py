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


from django.conf.urls.defaults import *

from projects.models import Project

# from groups.bridge import ContentBridge
#
#
# bridge = ContentBridge(Project, 'projects')

urlpatterns = patterns('projects.views',
    # url(r'^$', 'projects', name="project_list"),
    url(r'^create/$', 'create', name="project_create"),
    url(r'^your_projects/$', 'your_projects', name="your_projects"),
    url(r'^project/(?P<group_slug>[-\w]+)/$', 'project', name="project_detail"),
    # url(r'^project/(?P<group_slug>[-\w]+)/add_category$', 'add_category', name="add_category"),
    url(r'^project/(?P<group_slug>[-\w]+)/activate/$', 'activate', name="project_activate"),
    url(r'^project/(?P<group_slug>[-\w]+)/delete/$', 'delete', name="project_delete"),
    url(r'^project/(?P<group_slug>[-\w]+)/admin$', 'project_admin', name="project_admin"),
    url(r'^project/(?P<group_slug>[-\w]+)/fix_local_id$', 'fix_local_id', name="fix_local_id"),
    url(r'^project/(?P<group_slug>[-\w]+)/history$', 'project_history', name="project_history"),
    url(r'^project/(?P<group_slug>[-\w]+)/test_data/(?P<count>[0-9]+)', 'test_data'),
    url(r'^project/(?P<group_slug>[-\w]+)/(?P<iteration_id>[0-9]+)/burndown$', 'iteration_burndown'),
    url(r'^project/(?P<group_slug>[-\w]+)/burndown$', 'project_burndown'),
    url(r'^project/(?P<group_slug>[-\w]+)/remove_user$', 'remove_user', name="remove_user"),
    url(r'^project/(?P<group_slug>[-\w]+)/project_prediction$', 'project_prediction', name="project_prediction"),
    url(r'^project/(?P<group_slug>[-\w]+)/export$', 'export_project', name="export_project"),
    url(r'^project/(?P<group_slug>[-\w]+)/epics$', 'epics', name="epics"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration_list$', 'iteration_list', name="iteration_list"),
    url(r'^project/(?P<group_slug>[-\w]+)/all_iterations$', 'all_iterations', name="all_iterations"),
    url(r'^project/(?P<group_slug>[-\w]+)/search$', 'search_project', name="search_project"),
    

    # url(r'^project/(?P<group_slug>[-\w]+)/burnup_chart.png$', 'burnup_chart', name="burnup_chart"),

)

urlpatterns += patterns('projects.tags_views',
    url(r'^project/(?P<group_slug>[-\w]+)/tag/(?P<tag_name>.+)$', 'tag_detail', name="tag_detail"),
)

urlpatterns += patterns('projects.iteration_views',
    url(r'^project/(?P<group_slug>[-\w]+)/iteration_create$', 'iteration_create', name="iteration_create"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/delete', 'delete_iteration', name="delete_iteration"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/unlock$', 'unlock_iteration', name="unlock_iteration"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/import$', 'iteration_import', name="iteration_import"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/export$', 'iteration_export', name="iteration_export"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/report$', 'iteration_report', name="iteration_report"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/board$', 'scrum_board', name="scrum_board"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/iteration_stats$', 'iteration_stats', name="iteration_stats"),
    url(r'^project/(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)$', 'iteration', name="iteration"),

)


urlpatterns += patterns('projects.story_views',
    url(r'^story_permalink/(?P<story_id>[0-9]+)$', 'story_permalink', name="story_permalink"),
    url(r'^project/(?P<group_slug>[-\w]+)/stories/$', 'stories', name="stories"),
    url(r'^project/(?P<group_slug>[-\w]+)/stories/createAsync$', 'ajax_add_story', name="ajax_add_story"),
    url(r'^project/(?P<group_slug>[-\w]+)/epics/createAsync$', 'ajax_add_epic', name="ajax_add_epic"),
    url(r'^epic/(?P<epic_id>[0-9]+)$', 'epic', name="epic"),
    url(r'^epic/(?P<epic_id>[0-9]+)/edit', 'edit_epic', name="edit_epic"),
    url(r'^epic/(?P<epic_id>[0-9]+)/delete', 'delete_epic', name="delete_epic"),    
    url(r'^project/(?P<group_slug>[-\w]+)/stories/(?P<iteration_id>[0-9]+)/board/(?P<status>[-\w]+)$', 'stories_scrum_board', name="stories_scrum_board"),
    url(r'^project/(?P<group_slug>[-\w]+)/stories/(?P<iteration_id>[0-9]+)/(?P<page>[0-9]+)$', 'stories_iteration', name="stories_iteration"),
    url(r'^story/(?P<story_id>[0-9]+)/comments', 'story_comments'),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)/pretty', 'pretty_print_story'),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)/set_todo', 'set_story_status', {'status':1}),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)/set_doing', 'set_story_status', {'status':2}),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)/set_reviewing', 'set_story_status', {'status':3}),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)/set_done', 'set_story_status', {'status':4}),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)/scrum_board', 'scrum_board'),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)/reorder', 'reorder_story'),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)/delete', 'delete_story', name="delete_story"),    
    url(r'^project/(?P<group_slug>[-\w]+)/epic/(?P<epic_id>[0-9]+)/reorder', 'reorder_epic'),
    url(r'^story/(?P<story_id>[0-9]+)', 'story_block', name="story_block"),
    url(r'^project/(?P<group_slug>[-\w]+)/story/(?P<story_id>[0-9]+)', 'story_edit', name="story_form"),
    url(r'^project/(?P<group_slug>[-\w]+)/mini_story/(?P<story_id>[0-9]+)', 'mini_story'),
)

urlpatterns += patterns('projects.task_views',
    url(r'^task/create$', 'create_task', name="create_task"),
    url(r'^task/(?P<task_id>[0-9]+)/set_status$', 'set_task_status', name="set_task_status"),
    url(r'^task/(?P<task_id>[0-9]+)/delete$', 'delete_task', name="delete_task"),
    url(r'^task/(?P<task_id>[0-9]+)/edit$', 'edit_task', name="edit_task"),
)

# urlpatterns += bridge.include_urls('tasks.urls', r'^project/(?P<group_slug>[-\w]+)/tasks/')
