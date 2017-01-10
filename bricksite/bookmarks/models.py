from django.db import models
from django.contrib.auth.models import User

from django_extensions.db.models import TimeStampedModel

from products.models import Product


class Bookmark(TimeStampedModel):
    product = models.ForeignKey(Product)
    user = models.ForeignKey(User)

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)