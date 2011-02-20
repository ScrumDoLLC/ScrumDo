from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models



class Tip(models.Model):
    approved = models.BooleanField(  )
    tip_text = models.CharField( max_length=200 )
    creator = models.ForeignKey( User )