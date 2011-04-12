import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template import loader, Context

from activities.models import Activity, StoryActivity

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        for user in User.objects.all():
            if user.email_subscriptions.count() > 0:
                self.dailyDigest( user )
    
    def dailyDigest( self, user ):
        logger.debug( user )
        
        template = loader.get_template('activities/digest_header.html')
        context = Context( {"user":user } )        
        body = template.render(context)
        
        for sub in user.email_subscriptions.all():
            logger.debug(sub)
            today = datetime.date.today()
            mdiff = datetime.timedelta(days=-4) # TODO - change this to 1
            daterange = today + mdiff            
            stories = {}
            activities = Activity.objects.filter( project=sub.project, created__gte=daterange)
            for act in activities:
                act = act.mergeChildren()
                if hasattr(act,"story"):
                    stories[act.story.id] = act.story
            template = loader.get_template('activities/digest_project.html')
            context = Context( {"project":sub.project , "stories":stories} )        
            body = "%s %s" % (body, template.render(context))
        
        template = loader.get_template('activities/digest_footer.html')
        context = Context( {"user":user } )        
        body = "%s %s" % (body, template.render(context))
        logger.debug(body)

        
        
        

