import logging
from datetime import datetime

from .models import Item, ItemRecord

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def update_item_record(user):
    today = datetime.utcnow().date()
    items = Item.objects.filter(user=user)

    for item in items:
        record, created = ItemRecord.objects.get_or_create(item=item, created__date=today)
        record.quantity = item.quantity
        record.opened_quantity = item.thing_set.filter(opened=True).count()
        record.estimated_price = item.total_estimated
        record.estimated_profit = item.estimated_profit
        record.save()

    logger.info("SAVE ITEM HISTORIES: %s %s", user.username, items.count())
