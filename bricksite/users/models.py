from django.db import models
from django.db.models import Sum, Count
from django.conf import settings

from registration.signals import user_registered

from items.models import Item, Thing


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    is_trial = models.BooleanField(default=True)

    def theme_titles(self):
        return Item.objects.filter(user=self.user).values_list('product__theme_title', flat=True).distinct().order_by('product__theme_title')

    def item_count_by_theme(self):
        return Item.objects.filter(user=self.user).values('product__theme_title').annotate(count=Count('id'))

    def total_quantity_by_theme(self):
        return Thing.objects.filter(item__user=self.user).values('item__product__theme_title').annotate(count=Count('id'))

    def official_prices_by_theme(self):
        return Item.objects.filter(user=self.user).values('product__theme_title').annotate(official_price=Sum('product__official_price'))

    def total_estimated_by_theme(self):
        return Item.objects.filter(user=self.user).values('product__theme_title').annotate(official_price=Sum('total_estimated'))

    def __str__(self):
        return '{}'.format(self.user.username)

    class Meta:
        verbose_name = 'User Profile'


def user_registered_callback(sender, user, request, **kwargs):
    profile = UserProfile(user=user)
    profile.save()

user_registered.connect(user_registered_callback)