import logging
from datetime import datetime

from django.db import IntegrityError

from .items import ProductItem, EbayItem, BricklinkRecordItem
from products.models import Product, BricklinkRecord

logger = logging.getLogger()


class EbayPipeline(object):
    def process_item(self, item: EbayItem, spider):
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
            record = items[0]
            record.new_min_price = item.get('new_min_price')
            record.new_max_price = item.get('new_max_price')
            record.new_average_price = item.get('new_average_price')
            record.used_min_price = item.get('used_min_price')
            record.used_max_price = item.get('used_max_price')
            record.used_average_price = item.get('used_average_price')
            record.save()
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
            logger.info('Catch IntegrityError')
            product = Product.objects.get(product_code=item['product_code'])
            product.title = item['title']
            product.official_price = item.get('official_price', None)
            product.official_image_url = item.get('official_image_url', '')
            product.ages = item.get('ages', '')
            product.pieces = item.get('pieces', '')
            product.marketing_text = item.get('marketing_text', '')
            product.official_url = item.get('official_url', '')
            product.theme_title = item.get('theme_title', None)
            product.official_review_count = item.get('official_review_count', None)
            product.official_rating = item.get('official_rating', None)
            product.bricklink_url = item.get('bricklink_url', '')
            product.save()
            logger.info("Update: " + item['title'])
