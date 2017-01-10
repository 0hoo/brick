import time

from django.db import models
from django.db.models import Q
from django.urls import reverse

from django_extensions.db.models import TimeStampedModel


class ProductManager(models.Manager):
    def search(self, title_or_product_code):
        return self.filter(
            Q(title__icontains=title_or_product_code) | Q(product_code__icontains=title_or_product_code)
        ).order_by('title')[:10]


class Product(TimeStampedModel):
    product_code = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    official_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    official_image_url = models.URLField(blank=True)
    ages = models.CharField(max_length=255, blank=True)
    pieces = models.CharField(max_length=255, blank=True)
    marketing_text = models.TextField(blank=True)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse('products:detail', args=[str(self.id)])

    def last_bricklink_record(self):
        try:
            return self.bricklink_record_set.latest()
        except BricklinkRecord.DoesNotExist:
            return None

    def last_ebay_record(self):
        try:
            return self.ebay_record_set.latest()
        except EbayRecord.DoesNotExist:
            return None

    def get_absolute_url(self):
        return reverse('products:detail', args=[str(self.id)])

    def __str__(self):
        return '{} : {}'.format(self.title, self.product_code)


class ProductRecordModel(TimeStampedModel):
    new_min_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    new_max_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    new_average_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    used_min_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    used_max_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    used_average_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    @property
    def created_raw(self):
        return int(time.mktime(self.created.timetuple()) * 1000)

    class Meta:
        abstract = True


class BricklinkRecord(ProductRecordModel):
    product = models.ForeignKey(Product, related_name='bricklink_record_set')

    def __str__(self):
        return 'Bricklink: {} : {}'.format(self.product.title, self.created)

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = 'Bricklink Record'


class EbayRecord(ProductRecordModel):
    product = models.ForeignKey(Product, related_name='ebay_record_set')

    def __str__(self):
        return 'Ebay: {} : {}'.format(self.product.title, self.created)

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = 'Ebay Record'


class EbayItem(TimeStampedModel):
    product = models.ForeignKey(Product, related_name='ebay_item_set')
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    used = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return '[Used:{}] {}: {} {}'.format(self.used, self.product.product_number, self.price, self.title)

    class Meta:
        verbose_name = 'Ebay Item'
