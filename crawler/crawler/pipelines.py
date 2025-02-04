import logging
from datetime import datetime

from django.db.utils import IntegrityError

from .items import BrickSetItem, EbayEntryItem, BricklinkRecordItem
from sets.models import BrickSet, BricklinkRecord

logger = logging.getLogger()


class EbayPipeline(object):
    def process_item(self, item: EbayEntryItem, spider):
        item.save()
        return item


class BricklinkPipeline(object):
    def process_item(self, item: BricklinkRecordItem, spider):
        brickset = item['brickset']
        items = BricklinkRecord.objects.filter(created__date=datetime.utcnow().date(),
                                               brickset__brick_code=brickset.brick_code)

        brickset.bricklink_url = item.get('bricklink_url')
        brickset.save()

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


class LegoBrickSetPipeline(object):
    def process_item(self, item: BrickSetItem, spider):
        if not item['brick_code']:
            logger.warning("No product code: " + item['title'])
            return
        try:
            return item.save()
        except IntegrityError as e:
            logger.info('Catch IntegrityError')
            brickset = BrickSet.objects.get(brick_code=item['brick_code'])
            brickset.title = item['title']
            brickset.official_price = item.get('official_price', None)
            brickset.official_image_url = item.get('official_image_url', '')
            brickset.ages = item.get('ages', '')
            brickset.pieces = item.get('pieces', '')
            brickset.marketing_text = item.get('marketing_text', '')
            brickset.official_url = item.get('official_url', '')
            brickset.theme_title = item.get('theme_title', '')
            brickset.official_review_count = item.get('official_review_count', None)
            brickset.official_rating = item.get('official_rating', None)
            brickset.bricklink_url = item.get('bricklink_url', '')
            brickset.save()
            logger.info("Update: " + item['title'])


class BricksetDotComPricePipeline(object):
    def process_item(self, item: BrickSetItem, spider):
        brickset = BrickSet.objects.get(brick_code=item['brick_code'])
        if not brickset.official_price:
            brickset.official_price = item.get('official_price', None)
            if brickset.official_price:
                logger.info('Save from brickset.com: %s', (brickset.brick_code, brickset.official_price))
                brickset.save()
            else:
                logger.info('Skip: %s', (brickset.brick_code, brickset.official_price))
        return item


class BricksetDotComThemePipeline(object):
    def process_item(self, item: BrickSetItem, spider):
        brickset = BrickSet.objects.get(brick_code=item['brick_code'])
        if not brickset.theme_title:
            brickset.theme_title = item.get('theme_title', '')
            if brickset.theme_title:
                logger.info('Save from brickset.com: %s', (brickset.brick_code, brickset.theme_title))
                brickset.save()
            else:
                logger.info('Skip: %s', (brickset.brick_code, brickset.theme_title))
        return item
