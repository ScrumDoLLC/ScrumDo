import django.dispatch
                                                             

story_imported = django.dispatch.Signal(providing_args=["story","user"])