from django.db import models
from django.contrib.auth.models import User

from registration.signals import user_registered


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    is_trial = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.user.username)

    class Meta:
        verbose_name = 'User Profile'


def user_registered_callback(sender, user, request, **kwargs):
    print('user_registered_callback')
    profile = UserProfile(user=user)
    profile.save()

user_registered.connect(user_registered_callback)