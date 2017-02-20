from decimal import Decimal
from datetime import datetime

from .models import BrickSet, EbayRecord


def update_record_from_ebay():
    today = datetime.utcnow().date()

    for brickset in BrickSet.objects.all():
        ebay_entries = brickset.ebay_entry_set.filter(created__date=today)
        if ebay_entries.count() == 0:
            continue

        ebay_new_min_price = brickset.official_price
        ebay_new_max_price = 0
        ebay_new_average_price = 0
        ebay_used_min_price = brickset.official_price
        ebay_used_max_price = 0
        ebay_used_average_price = 0
        new_sum = 0
        used_sum = 0
        items_to_delete = []
        new_count = 0
        used_count = 0

        for ebay_entry in ebay_entries:
            if not ebay_entry.price or \
                    (not ebay_entry.used and ebay_entry.price < (brickset.official_price / Decimal(3.0))) or \
                    (ebay_entry.used and ebay_entry.price < (brickset.official_price / Decimal(5.0))):
                items_to_delete.append(ebay_entry)
                continue

            if ebay_entry.used:
                ebay_used_min_price = min(ebay_used_min_price, ebay_entry.price)
                ebay_used_max_price = max(ebay_used_max_price, ebay_entry.price)
                used_sum += ebay_entry.price
                used_count += 1
            else:
                ebay_new_min_price = min(ebay_new_min_price, ebay_entry.price)
                ebay_new_max_price = max(ebay_new_max_price, ebay_entry.price)
                new_sum += ebay_entry.price
                new_count += 1

        if new_count > 0:
            ebay_new_average_price = new_sum / new_count

        if used_count > 0:
            ebay_used_average_price = used_sum / used_count

        for item in items_to_delete:
            item.delete()

        if new_count > 0 or used_count > 0:
            record, created = EbayRecord.objects.get_or_create(brickset=brickset, created__date=today)
            record.new_min_price = ebay_new_min_price
            record.new_max_price = ebay_new_max_price
            record.new_average_price = ebay_new_average_price
            record.used_min_price = ebay_used_min_price
            record.used_max_price = ebay_used_max_price
            record.used_average_price = ebay_used_average_price
            record.save()
