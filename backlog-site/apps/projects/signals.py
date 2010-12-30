import django.dispatch
                                                             
# Signal dispatched when a story is edited. (Not including status changes, see next signal)
# user = who did it, story = the story that changed.
story_updated = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story's status is changed.
# user = who did it, story = the story that changed.
story_status_changed = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story is deleted
# user = who did it, story = the story that changed.
story_deleted = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story is created
# user = who did it, story = the story that changed.
story_created = django.dispatch.Signal(providing_args=["story","user"])
