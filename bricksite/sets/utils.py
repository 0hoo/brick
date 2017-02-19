from decimal import Decimal
from datetime import datetime

from .models import BrickSet, EbayRecord


def update_record_from_ebay():
    today = datetime.utcnow().date()

    for product in BrickSet.objects.all():
        ebay_items = product.ebay_item_set.filter(created__date=today)
        if ebay_items.count() == 0:
            continue

        ebay_new_min_price = product.official_price
        ebay_new_max_price = 0
        ebay_new_average_price = 0
        ebay_used_min_price = product.official_price
        ebay_used_max_price = 0
        ebay_used_average_price = 0
        new_sum = 0
        used_sum = 0
        items_to_delete = []
        new_count = 0
        used_count = 0

        for ebay_item in ebay_items:
            if not ebay_item.price or \
                    (not ebay_item.used and ebay_item.price < (product.official_price / Decimal(3.0))) or \
                    (ebay_item.used and ebay_item.price < (product.official_price / Decimal(5.0))):
                items_to_delete.append(ebay_item)
                continue

            if ebay_item.used:
                ebay_used_min_price = min(ebay_used_min_price, ebay_item.price)
                ebay_used_max_price = max(ebay_used_max_price, ebay_item.price)
                used_sum += ebay_item.price
                used_count += 1
            else:
                ebay_new_min_price = min(ebay_new_min_price, ebay_item.price)
                ebay_new_max_price = max(ebay_new_max_price, ebay_item.price)
                new_sum += ebay_item.price
                new_count += 1

        if new_count > 0:
            ebay_new_average_price = new_sum / new_count

        if used_count > 0:
            ebay_used_average_price = used_sum / used_count

        for item in items_to_delete:
            item.delete()

        if new_count > 0 or used_count > 0:
            record, created = EbayRecord.objects.get_or_create(brickset=product, created__date=today)
            record.new_min_price = ebay_new_min_price
            record.new_max_price = ebay_new_max_price
            record.new_average_price = ebay_new_average_price
            record.used_min_price = ebay_used_min_price
            record.used_max_price = ebay_used_max_price
            record.used_average_price = ebay_used_average_price
            record.save()
