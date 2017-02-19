import logging
from datetime import datetime

from .models import MyBrick, MyBrickRecord

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def update_mybrick_record(user):
    today = datetime.utcnow().date()
    mybricks = MyBrick.objects.filter(user=user)

    for mybrick in mybricks:
        record, created = MyBrickRecord.objects.get_or_create(mybrick=mybrick, created__date=today)
        record.quantity = mybrick.quantity
        record.opened_quantity = mybrick.thing_set.filter(opened=True).count()
        record.estimated_price = mybrick.total_estimated
        record.estimated_profit = mybrick.estimated_profit
        record.save()

    logger.info("SAVE MYBRICK RECORDS: %s %s", user.username, mybricks.count())
