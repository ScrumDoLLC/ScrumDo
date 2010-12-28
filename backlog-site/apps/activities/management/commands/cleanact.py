
from optparse import make_option
import datetime
from  django.core.management.base import BaseCommand
from activities.models import SubjectActivity

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--purge', action='store_true', dest='purge', default=False,
            help='Generate evolutions to delete stale applications.'),
    )


    help = 'Purge old Subject Activities'

    def handle(self, *app_labels, **options):
        self.purge(*app_labels, **options)

    def purge(self, *app_labels, **options):
        print 'Purging Activities'
        SubjectActivity.purgeMonthOld()
