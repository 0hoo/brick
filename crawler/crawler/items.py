import scrapy
from scrapy_djangoitem import DjangoItem

from sets.models import BrickSet, BricklinkRecord, EbayItem


class ProductItem(DjangoItem):
    django_model = Product


class BricklinkRecordItem(DjangoItem):
    django_model = BricklinkRecord
    bricklink_url = scrapy.Field()


class EbayItem(DjangoItem):
    django_model = EbayItem
