from django.conf.urls.defaults import *
from account.forms import *

urlpatterns = patterns('',
    url(r'^add/(?P<favorite_type>[0-9]+)/(?P<favorite_id>[0-9]+)$', 'favorites.views.add', name="add_favorite"),
    url(r'^remove/(?P<favorite_type>[0-9]+)/(?P<favorite_id>[0-9]+)$', 'favorites.views.remove', name="remove_favorite"),
)
