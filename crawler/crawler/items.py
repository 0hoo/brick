import scrapy
from scrapy_djangoitem import DjangoItem

from sets.models import BrickSet, BricklinkRecord, EbayEntry


class BrickSetItem(DjangoItem):
    django_model = BrickSet


class BricklinkRecordItem(DjangoItem):
    django_model = BricklinkRecord
    bricklink_url = scrapy.Field()


class EbayEntryItem(DjangoItem):
    django_model = EbayEntry
