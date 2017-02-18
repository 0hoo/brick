from django.db import models
from django.contrib.auth.models import User

from django_extensions.db.models import TimeStampedModel

from sets.models import BrickSet


class Bookmark(TimeStampedModel):
    product = models.ForeignKey(BrickSet)
    user = models.ForeignKey(User, related_name='bookmark_set')

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)