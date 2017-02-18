from collections import Counter

from django.db import models
from django.db.models import Sum, Count
from django.contrib.auth.models import User

from django_extensions.db.models import TimeStampedModel

from mybricks.models import Item, Thing


class Dashboard(TimeStampedModel):
    user = models.ForeignKey(User, related_name='dashboard_set')

    item_count = models.PositiveIntegerField()
    item_quantity = models.PositiveIntegerField()
    sold_quantity = models.PositiveIntegerField()
    bookmarked_item_count = models.PositiveIntegerField()

    total_buying_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_estimated_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_profit = models.DecimalField(max_digits=8, decimal_places=2)
    total_official_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_target_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_sold_price = models.DecimalField(max_digits=8, decimal_places=2)

    target_at = models.DateField()

    def __str__(self):
        return '{} dashboard: {}'.format(self.user.username, self.target_at)

    class Meta:
        verbose_name = 'Dashboard'
        get_latest_by = 'target_at'
        ordering = ('-target_at',)


def theme_titles(user):
    return Item.objects.filter(user=user).values_list('product__theme_title', flat=True).distinct().order_by('product__theme_title')


def item_count_by_theme(user):
    return Item.objects.filter(user=user).values('product__theme_title').annotate(count=Count('id')).order_by('-count')


def item_quantity_by_theme(user):
    return Thing.objects.filter(item__user=user).values('item__product__theme_title').annotate(count=Count('id')).order_by('-count')


def official_price_by_theme(user):
    return Item.objects.filter(user=user).values('product__theme_title').annotate(official_price=Sum('product__official_price')).order_by('-official_price')


def total_prices_by_theme(user):
    estimated_counter = Counter()
    profit_counter = Counter()
    buying_price_counter = Counter()
    sold_quantity_counter = Counter()
    sold_price_counter = Counter()
    for item in Item.objects.filter(user=user):
        estimated_counter[item.product.theme_title] += item.total_estimated
        profit_counter[item.product.theme_title] += item.estimated_profit
        buying_price_counter[item.product.theme_title] += item.total_buying_price
        if item.sold_quantity:
            sold_quantity_counter[item.product.theme_title] += item.sold_quantity
        if item.total_sold_price:
            sold_price_counter[item.product.theme_title] += item.total_sold_price
    return estimated_counter.most_common(), profit_counter.most_common(), buying_price_counter.most_common(), sold_quantity_counter.most_common(), sold_price_counter.most_common()
