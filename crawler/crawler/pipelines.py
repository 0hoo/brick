import logging
from datetime import datetime

from django.db import IntegrityError

from .items import ProductItem, EbayRecordItem, BricklinkRecordItem
from products.models import BricklinkRecord

logger = logging.getLogger()


class EbayPipeline(object):
    def process_item(self, item: EbayRecordItem, spider):
        item.save()
        return item


class BricklinkPipeline(object):
    def process_item(self, item: BricklinkRecordItem, spider):
        product = item['product']
        items = BricklinkRecord.objects.filter(created__date=datetime.utcnow().date(),
                                               product__product_code=product.product_code)

        product.last_min_price = item.get('new_min_price')
        product.last_max_price = item.get('new_max_price')
        product.last_average_price = item.get('new_average_price')
        product.save()

        if len(items) > 0:
            logger.debug('UPDATE EXIST HISTORY')
            history = items[0]
            history.new_min_price = item.get('new_min_price')
            history.new_max_price = item.get('new_max_price')
            history.new_average_price = item.get('new_average_price')
            history.used_min_price = item.get('used_min_price')
            history.used_max_price = item.get('used_max_price')
            history.used_average_price = item.get('used_average_price')
            history.save()
        else:
            logger.debug('SAVE NEW HISTORY')
            item.save()

        return item


class ProductPipeline(object):
    def process_item(self, item: ProductItem, spider):
        if not item['product_code']:
            logger.warn("No product code: " + item['title'])
            return
        try:
            return item.save()
        except IntegrityError as e:
            logger.info("Duplicate - Skip: " + item['title'])
