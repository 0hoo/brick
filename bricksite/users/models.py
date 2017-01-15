from django.db import models
from django.conf import settings

from registration.signals import user_registered

from items.models import Item


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    is_trial = models.BooleanField(default=True)

    def theme_titles(self):
        return Item.objects.filter(user=self.user).values_list('product__theme_title', flat=True).distinct().order_by('product__theme_title')

    def __str__(self):
        return '{}'.format(self.user.username)

    class Meta:
        verbose_name = 'User Profile'


def user_registered_callback(sender, user, request, **kwargs):
    profile = UserProfile(user=user)
    profile.save()

user_registered.connect(user_registered_callback)