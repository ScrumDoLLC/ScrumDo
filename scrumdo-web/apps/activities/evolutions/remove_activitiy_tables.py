from django_evolution.mutations import *
from django.db import models

MUTATIONS = [     
     DeleteModel('TextActivity'),
     DeleteModel('StoryActivity'),
     DeleteModel('CommentActivity'),
     DeleteModel('PointsChangeActivity'),
     DeleteModel('IterationActivity'),
     DeleteModel('DeletedActivity'),
     DeleteModel('Activity'),
     DeleteModel('ActivityAction'),     
]