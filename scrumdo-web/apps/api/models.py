import uuid
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, date
import hmac
try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

def generate_key():
    # Get a random UUID.
    new_uuid = uuid.uuid4()
    # Hmac that beast.
    return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()

class DeveloperApiKey(models.Model):
    developer = models.ForeignKey(User, related_name='developer_key')
    key = models.CharField(max_length=256, blank=True, default='')
    application_name = models.CharField(max_length=30)
    created = models.DateTimeField(default=datetime.now)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s for developer %s" % (self.key, self.developer)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_key()

        return super(DeveloperApiKey, self).save(*args, **kwargs)


class UserApiKey(models.Model):
    user = models.ForeignKey(User, related_name='api_key')
    key = models.CharField(max_length=256, blank=True, default='')
    developer_key = models.ForeignKey(DeveloperApiKey,related_name="user_key")

    created = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return u"%s for %s" % (self.key, self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_key()

        return super(UserApiKey, self).save(*args, **kwargs)
