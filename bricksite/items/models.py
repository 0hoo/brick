import time
from django.db import models
from django.db.models import Avg, Sum
from django.urls import reverse
from django.contrib.auth.models import User

from django_extensions.db.models import TimeStampedModel

from products.models import Product


class Item(TimeStampedModel):
    product = models.ForeignKey(Product)
    user = models.ForeignKey(User)
    target_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    @property
    def quantity(self):
        return self.thing_set.filter(sold=False).count()

    @property
    def sold_quantity(self):
        return self.thing_set.filter(sold=True).count()

    @property
    def average_sold_price(self):
        return self.thing_set.exclude(sold_price__isnull=True).aggregate(Avg('sold_price'))['sold_price__avg']

    @property
    def total_sold_price(self):
        return self.thing_set.exclude(sold_price__isnull=True).aggregate(Sum('sold_price'))['sold_price__sum']

    @property
    def average_buying_price(self):
        return self.thing_set.exclude(buying_price__isnull=True).aggregate(Avg('buying_price'))['buying_price__avg']

    @property
    def total_buying_price(self):
        return self.thing_set.exclude(buying_price__isnull=True).aggregate(Sum('buying_price'))['buying_price__sum']

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
        things, last_bricklink_record, last_ebay_record = (self.thing_set.unsold(),
                                                           self.product.last_bricklink_record(),
                                                           self.product.last_ebay_record())
        things_count = things.count()
        new_price = last_bricklink_record.new_average_price if last_bricklink_record and last_bricklink_record.new_average_price else \
            (last_ebay_record.new_average_price if last_ebay_record and last_ebay_record.new_average_price else
             self.product.official_price)

        if things_count > 0:
            opened_count = sum(t.opened for t in things)
            unopned_count = things_count - opened_count
            used_price = last_bricklink_record.used_average_price if last_bricklink_record and last_bricklink_record.used_average_price else \
                (last_ebay_record.used_average_price if last_ebay_record and last_ebay_record.used_average_price else
                 self.product.official_price)
            return unopned_count * new_price + opened_count * used_price
        else:
            return new_price * self.quantity

    def get_absolute_url(self):
        return reverse('items:detail', args=[str(self.id)])

    def __str__(self):
        return '{} {} {}'.format(self.user.username, self.product.product_code, self.product.title)

    class Meta:
        unique_together = ['product', 'user']


class ItemRecord(TimeStampedModel):
    item = models.ForeignKey(Item, related_name='record_set')
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


class ThingManager(models.Manager):
    def unsold(self):
        return self.filter(sold=False)

    def sold(self):
        return self.filter(sold=True)


class Thing(TimeStampedModel):
    item = models.ForeignKey(Item, related_name='thing_set')
    buying_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    opened = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)
    sold = models.BooleanField(default=False)
    sold_at = models.DateField(null=True, blank=True)
    sold_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    objects = ThingManager()

    @property
    def opened_text(self):
        return 'opened' if self.opened else 'unopened'

    def __str__(self):
        return '{} - {} {}'.format(self.item.product.title, "Opened" if self.opened else "Unopened", self.buying_price)

    class Meta:
        verbose_name = 'Thing'
