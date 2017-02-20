import scrapy
from scrapy_djangoitem import DjangoItem

from sets.models import BrickSet, BricklinkRecord, EbayItem


class BrickSetItem(DjangoItem):
    django_model = BrickSet


class BricklinkRecordItem(DjangoItem):
    django_model = BricklinkRecord
    bricklink_url = scrapy.Field()


class EbayItem(DjangoItem):
    django_model = EbayItem
