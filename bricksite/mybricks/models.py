import time
from collections import namedtuple

from django.db import models
from django.db.models import Avg, Sum
from django.urls import reverse
from django.contrib.auth.models import User

from django_extensions.db.models import TimeStampedModel

from sets.models import BrickSet


class ItemManager(models.Manager):
    def user_has_item(self, user, product):
        existing_items = self.filter(product=product).filter(user=user)
        if existing_items.count() > 0:
            return existing_items[0]
        return None


Estimation = namedtuple('Estimation', ['price', 'unopened_count', 'opened_count', 'new_price', 'new_price_source', 'total_new_price', 'used_price', 'used_price_source', 'total_used_price'])


class MyBrick(TimeStampedModel):
    brickset = models.ForeignKey(BrickSet)
    user = models.ForeignKey(User)
    target_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    objects = ItemManager()

    @property
    def quantity(self):
        return self.thing_set.filter(sold=False).count()

    @property
    def sold_quantity(self):
        return self.thing_set.filter(sold=True).count()

    @property
    def average_sold_price(self):
        return self.thing_set.exclude(sold_price__isnull=True).exclude(sold=False).aggregate(Avg('sold_price'))['sold_price__avg']

    @property
    def total_sold_price(self):
        return self.thing_set.exclude(sold_price__isnull=True).exclude(sold=False).aggregate(Sum('sold_price'))['sold_price__sum']

    @property
    def average_buying_price(self):
        return self.thing_set.exclude(buying_price__isnull=True).exclude(sold=True).aggregate(Avg('buying_price'))['buying_price__avg']

    @property
    def total_buying_price(self):
        return self.thing_set.exclude(buying_price__isnull=True).exclude(sold=True).aggregate(Sum('buying_price'))['buying_price__sum']

    @property
    def estimated_total_buying_price(self):
        return sum((thing.buying_price or self.product.official_price for thing in self.thing_set.unsold()))

    @property
    def estimated_profit(self):
        return self.total_estimated - self.estimated_total_buying_price

    @property
    def buying_average_price(self):
        return self.total_buying_price / self.quantity

    @property
    def total_estimated(self):
        return self.estimation.price
        prices = self.estimated_new_old_price
        new_price, used_price = prices[0][0], prices[1][0]
        return self.thing_set.unopened().count() * new_price + self.thing_set.opened().count() * used_price

    @property
    def estimation(self) -> Estimation:
        last_bricklink_record, last_ebay_record = (self.product.last_bricklink_record(), self.product.last_ebay_record())
        if last_bricklink_record and last_bricklink_record.new_average_price:
            new_price = last_bricklink_record.new_average_price
            new_price_source = 'Bricklink'
        elif last_ebay_record and last_ebay_record.new_average_price:
            new_price = last_ebay_record.new_average_price
            new_price_source = 'eBay'
        else:
            new_price = self.product.official_price
            new_price_source = 'Official'

        if last_bricklink_record and last_bricklink_record.used_average_price:
            used_price = last_bricklink_record.used_average_price
            used_price_source = 'Bricklink'
        elif last_ebay_record and last_ebay_record.used_average_price:
            used_price = last_ebay_record.used_average_price
            used_price_source = 'eBay'
        else:
            used_price = self.product.official_price
            used_price_source = 'Official'

        unopened_count = self.thing_set.unopened().count()
        opened_count = self.thing_set.opened().count()
        total_new_price = unopened_count * new_price
        total_used_price = opened_count * used_price
        price = total_new_price + total_used_price
        return Estimation(price=price, unopened_count=unopened_count, opened_count=opened_count,
                          new_price=new_price, new_price_source=new_price_source, total_new_price=total_new_price,
                          used_price=used_price, used_price_source=used_price_source, total_used_price=total_used_price)

    def get_absolute_url(self):
        return reverse('mybricks:detail', args=[str(self.id)])

    def __str__(self):
        return '{} {} {}'.format(self.user.username, self.product.brick_code, self.product.title)

    class Meta:
        unique_together = ['brickset', 'user']


class MyBrickRecord(TimeStampedModel):
    item = models.ForeignKey(MyBrick, related_name='record_set')
    quantity = models.PositiveIntegerField(default=1)
    opened_quantity = models.PositiveIntegerField(default=0)
    estimated_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_profit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    @property
    def created_raw(self):
        return int(time.mktime(self.created.timetuple()) * 1000)

    def __str__(self):
        return '{} {} Record {}'.format(self.item.user.username, self.item.product.title, self.created)

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = 'Item Record'


class MyBrickItemManager(models.Manager):
    def get_queryset(self):
        return super(MyBrickItemManager, self).get_queryset().order_by('sold')

    def unopened(self):
        return self.filter(sold=False, opened=False)

    def opened(self):
        return self.filter(sold=False, opened=True)

    def unsold(self):
        return self.filter(sold=False)

    def sold(self):
        return self.filter(sold=True)


class MyBrickItem(TimeStampedModel):
    item = models.ForeignKey(MyBrick, related_name='thing_set')
    buying_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    opened = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)
    sold = models.BooleanField(default=False)
    sold_at = models.DateField(null=True, blank=True)
    sold_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    objects = MyBrickItemManager()

    @property
    def opened_text(self):
        return 'opened' if self.opened else 'unopened'

    def __str__(self):
        return '{} - {} {}'.format(self.item.product.title, "Opened" if self.opened else "Unopened", self.buying_price)

    class Meta:
        verbose_name = 'Thing'
