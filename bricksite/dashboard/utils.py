import logging
from datetime import datetime

from items.models import Item
from .models import Dashboard

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def snapshot_latest_dashboard(user):
    items = Item.objects.filter(user=user)

    item_quantity = 0

    total_buying_price = 0
    total_estimated_price = 0
    total_profit = 0
    total_official_price = 0
    total_target_price = 0

    new_min_price = 0
    new_max_price = 0
    new_average_price = 0
    used_min_price = 0
    used_max_price = 0
    used_average_price = 0

    new_min_ebay_price = 0
    new_max_ebay_price = 0
    new_average_ebay_price = 0
    used_min_ebay_price = 0
    used_max_ebay_price = 0
    used_average_ebay_price = 0

    for item in items:
        official_price = item.product.official_price

        item_quantity += item.quantity
        total_buying_price += float(item.total_buying_price or 0)
        total_estimated_price += item.total_estimated
        total_profit += item.estimated_profit
        total_official_price += float(official_price * item.quantity)
        total_target_price += float(item.target_price or 0) * item.quantity

        def total(h, attr):
            return (getattr(h, attr) if getattr(h, attr) else official_price) * item.quantity

        record = item.product.last_bricklink_record()
        if record:
            new_min_price += total(record, 'new_min_price')
            new_max_price += total(record, 'new_max_price')
            new_average_price = total(record, 'new_average_price')
            used_min_price += total(record, 'used_min_price')
            used_max_price += total(record, 'used_max_price')
            used_average_price += total(record, 'used_average_price')

        record = item.product.last_ebay_record()
        if record:
            new_min_ebay_price += total(record, 'new_min_price')
            new_max_ebay_price += total(record, 'new_max_price')
            new_average_ebay_price += total(record, 'new_average_price')
            used_min_ebay_price += total(record, 'used_min_price')
            used_max_ebay_price += total(record, 'used_max_price')
            used_average_ebay_price += total(record, 'used_average_price')

    today = datetime.utcnow().date()
    exists = Dashboard.objects.filter(user=user, target_at=today)
    if exists.count() > 0:
        dashboard = exists[0]
    else:
        dashboard = Dashboard()

    dashboard.user = user
    dashboard.item_count = len(items)
    dashboard.item_quantity = item_quantity
    dashboard.total_buying_price = total_buying_price
    dashboard.total_estimated_price = total_estimated_price
    dashboard.total_profit = total_profit
    dashboard.total_official_price = total_official_price
    dashboard.total_target_price = total_target_price

    dashboard.new_min_price = new_min_price
    dashboard.new_max_price = new_max_price
    dashboard.new_average_price = new_average_price
    dashboard.used_min_price = used_min_price
    dashboard.used_max_price = used_max_price
    dashboard.used_average_price = used_average_price

    dashboard.new_min_ebay_price = new_min_ebay_price
    dashboard.new_max_ebay_price = new_max_ebay_price
    dashboard.new_average_ebay_price = new_average_ebay_price
    dashboard.used_min_ebay_price = used_min_ebay_price
    dashboard.used_max_ebay_price = used_max_ebay_price
    dashboard.used_average_ebay_price = used_average_ebay_price

    dashboard.target_at = today
    dashboard.bookmarked_item_count = 0
    dashboard.save()
    logger.info("SAVE DASHBOARD: %s" % user.username)
    return dashboard
