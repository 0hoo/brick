from scrapy_djangoitem import DjangoItem

from products.models import Product, BricklinkRecord, EbayRecord


class ProductItem(DjangoItem):
    django_model = Product


class BricklinkRecordItem(DjangoItem):
    django_model = BricklinkRecord


class EbayRecordItem(DjangoItem):
    django_model = EbayRecord
