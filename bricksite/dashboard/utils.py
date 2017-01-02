import logging
from datetime import datetime
from django.db.models import Sum

from items.models import Item
from .models import Dashboard

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def snapshot_latest_dashboard(user):
    items = Item.objects.filter(user=user)
    owned = items.filter(owned=True)

    total_estimated_price = 0
    total_profit = 0
    total_official_price = 0
    owned_official_price = 0
    owned_buying_price = 0
    total_target_price = 0
    owned_target_price = 0

    owned_new_min_price = 0
    owned_new_max_price = 0
    owned_new_average_price = 0
    owned_used_min_price = 0
    owned_used_max_price = 0
    owned_used_average_price = 0

    owned_new_min_ebay_price = 0
    owned_new_max_ebay_price = 0
    owned_new_average_ebay_price = 0
    owned_used_min_ebay_price = 0
    owned_used_max_ebay_price = 0
    owned_used_average_ebay_price = 0

    for item in items:
        total_estimated_price += item.total_estimated
        total_profit += item.estimated_profit

        value = float(item.product.official_price * item.quantity)
        total_official_price += value
        owned_official_price += value if item.owned else 0

        buying_value = float(item.buying_price or 0) * item.quantity
        owned_buying_price += buying_value if item.owned else 0

        target_price = float(item.target_price or 0)
        total_target_price += target_price
        owned_target_price += target_price if item.owned else 0

        record = item.product.last_bricklink_record()
        official_price = item.product.official_price

        def owned_total(h, attr):
            return ((getattr(h, attr) if getattr(h, attr) else official_price) * item.quantity) if item.owned else 0

        if record:
            owned_new_min_price += owned_total(record, 'new_min_price')
            owned_new_max_price += owned_total(record, 'new_max_price')
            owned_new_average_price += owned_total(record, 'new_average_price')
            owned_used_min_price += owned_total(record, 'used_min_price')
            owned_used_max_price += owned_total(record, 'used_max_price')
            owned_used_average_price += owned_total(record, 'used_average_price')

        record = item.product.last_ebay_record()
        if record:
            owned_new_min_price += owned_total(record, 'new_min_price')
            owned_new_max_price += owned_total(record, 'new_max_price')
            owned_new_average_price += owned_total(record, 'new_average_price')
            owned_used_min_price += owned_total(record, 'used_min_price')
            owned_used_max_price += owned_total(record, 'used_max_price')
            owned_used_average_price += owned_total(record, 'used_average_price')

    today = datetime.utcnow().date()
    exists = Dashboard.objects.filter(user=user, target_at=today)
    if exists.count() > 0:
        dashboard = exists[0]
    else:
        dashboard = Dashboard()
    dashboard.user = user
    dashboard.owned_count = owned.count()
    dashboard.owned_quantity = owned.aggregate(Sum('quantity'))['quantity__sum'] or 0

    dashboard.total_estimated_price = total_estimated_price
    dashboard.total_profit = total_profit
    dashboard.total_official_price = total_official_price
    dashboard.owned_official_price = owned_official_price
    dashboard.owned_buying_price = owned_buying_price
    dashboard.total_target_price = total_target_price
    dashboard.owned_target_price = owned_target_price

    dashboard.owned_new_min_price = owned_new_min_price
    dashboard.owned_new_max_price = owned_new_max_price
    dashboard.owned_new_average_price = owned_new_average_price
    dashboard.owned_used_min_price = owned_used_min_price
    dashboard.owned_used_max_price = owned_used_max_price
    dashboard.owned_used_average_price = owned_used_average_price

    dashboard.owned_new_min_ebay_price = owned_new_min_ebay_price
    dashboard.owned_new_max_ebay_price = owned_new_max_ebay_price
    dashboard.owned_new_average_ebay_price = owned_new_average_ebay_price
    dashboard.owned_used_min_ebay_price = owned_used_min_ebay_price
    dashboard.owned_used_max_ebay_price = owned_used_max_ebay_price
    dashboard.owned_used_average_ebay_price = owned_used_average_ebay_price

    dashboard.target_at = today
    dashboard.save()
    logger.info("SAVE DASHBOARD: %s" % user.username)
    return dashboard
