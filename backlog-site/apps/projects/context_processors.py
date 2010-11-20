from django.conf import settings # import the settings file


def projects_constants(context):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'GOOGLE_ANALYTICS': settings.GOOGLE_ANALYTICS,
            'GOOGLE_ANALYTICS_ACCOUNT': settings.GOOGLE_ANALYTICS_ACCOUNT }
