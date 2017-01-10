from scrapy_djangoitem import DjangoItem

from products.models import Product, BricklinkRecord, EbayItem


class ProductItem(DjangoItem):
    django_model = Product


class BricklinkRecordItem(DjangoItem):
    django_model = BricklinkRecord


class EbayItem(DjangoItem):
    django_model = EbayItem
