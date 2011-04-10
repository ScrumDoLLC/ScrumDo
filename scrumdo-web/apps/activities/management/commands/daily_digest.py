import datetime
from  django.core.management.base import BaseCommand
from activities.models import Activity

class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        pass

