# 
# 
# from optparse import make_option
# import datetime
# from  django.core.management.base import BaseCommand
# from activities.models import Activity
# 
# class Command(BaseCommand):
#     def handle(self, *app_labels, **options):
#         activities = Activity.objects.all()
#         for activity in activities:
#             activity = activity.mergeChildren()
#             activity.real_type = activity._get_real_type()
#             activity.save()
