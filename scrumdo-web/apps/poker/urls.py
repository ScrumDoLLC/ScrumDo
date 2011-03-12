from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('poker.views',
    url(r'^play/(?P<project_slug>[-\w]+)$', "play", name="play_poker"),
    url(r'^ajax/(?P<project_slug>[-\w]+)$', "ajax", name="poker_ajax"),
    url(r'^hookbox_test$', "hookbox_test"),
    url(r'^hookbox_callback/connect$', "hookbox_callback_connect"),
    url(r'^hookbox_callback/subscribe$', "hookbox_callback_subscribe"),
    url(r'^hookbox_callback/unsubscribe$', "hookbox_callback_unsubscribe"),
    url(r'^hookbox_callback/publish$', "hookbox_callback_publish"),
    url(r'^hookbox_callback/create_channel$', "hookbox_callback_create_channel"),
    url(r'^hookbox_callback/disconnect$', "hookbox_callback_disconnect"),
    url(r'^hookbox_callback/destroy_channel$', "hookbox_callback_destroy_channel"),

)
