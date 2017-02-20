import time

from django.db import models
from django.db.models import Q
from django.urls import reverse

from django_extensions.db.models import TimeStampedModel


class BrickSetManager(models.Manager):
    def search(self, title_or_brick_code):
        return self.filter(
            Q(title__icontains=title_or_brick_code) | Q(brick_code__icontains=title_or_brick_code)
        ).order_by('title')[:10]

    def theme_titles(self):
        return self.values_list('theme_title', flat=True).distinct().order_by('theme_title')


class BrickSet(TimeStampedModel):
    brick_code = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    official_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    official_image_url = models.URLField(blank=True)
    ages = models.CharField(max_length=255, blank=True)
    pieces = models.CharField(max_length=255, blank=True)
    marketing_text = models.TextField(blank=True)
    official_url = models.URLField(blank=True)
    theme_title = models.CharField(max_length=255, blank=True)
    official_review_count = models.PositiveIntegerField(null=True, blank=True)
    official_rating = models.FloatField(null=True, blank=True)
    bricklink_url = models.URLField(blank=True)
    is_approved = models.BooleanField(default=False)

    objects = BrickSetManager()

    def get_absolute_url(self):
        return reverse('sets:detail', args=[str(self.id)])

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
        return reverse('sets:detail', args=[str(self.id)])

    def __str__(self):
        return '{} : {}'.format(self.title, self.brick_code)

    class Meta:
        verbose_name = 'Brick Set'


class BrickSetRecordModel(TimeStampedModel):
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


class BricklinkRecord(BrickSetRecordModel):
    brickset = models.ForeignKey(BrickSet, related_name='bricklink_record_set')

    def __str__(self):
        return 'Bricklink: {} : {}'.format(self.brickset.title, self.created)

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = 'Bricklink Record'


class EbayRecord(BrickSetRecordModel):
    brickset = models.ForeignKey(BrickSet, related_name='ebay_record_set')

    def __str__(self):
        return 'eBay: {} : {}'.format(self.brickset.title, self.created)

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = 'ebay Record'


class EbayEntryManager(models.Manager):
    def get_queryset(self):
        return super(EbayEntryManager, self).get_queryset().order_by('-price')


class EbayEntry(TimeStampedModel):
    brickset = models.ForeignKey(BrickSet, related_name='ebay_entry_set')
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    used = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    available = models.CharField(max_length=255, null=True, blank=True)

    objects = EbayEntryManager()

    @property
    def available_text(self):
        if not self.available:
            return ''
        if self.available.lower().startswith('more than 10 '):
            return '10+'
        elif self.available.lower().startswith('limited '):
            return 'Limited'
        comp = self.available.split(' ')
        if len(comp) > 1:
            try:
                return int(comp[0])
            except ValueError:
                return self.available
        return self.available

    def __str__(self):
        return '[Used:{}] {}: {} {}'.format(self.used, self.brickset.brick_code, self.price, self.title)

    class Meta:
        verbose_name = 'eBay Item'
