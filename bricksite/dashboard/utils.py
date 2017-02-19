import logging
from datetime import datetime

from mybricks.models import MyBrick
from .models import Dashboard

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def snapshot_latest_dashboard(user):
    mybricks = MyBrick.objects.filter(user=user)

    item_quantity = 0
    sold_quantity = 0

    total_buying_price = 0
    total_estimated_price = 0
    total_profit = 0
    total_official_price = 0
    total_target_price = 0
    total_sold_price = 0

    for mybrick in mybricks:
        official_price = mybrick.brickset.official_price

        item_quantity += mybrick.quantity
        sold_quantity += mybrick.sold_quantity

        total_buying_price += float(mybrick.total_buying_price or 0)
        total_estimated_price += mybrick.total_estimated
        total_profit += mybrick.estimated_profit
        total_official_price += float(official_price * mybrick.quantity)
        total_target_price += float(mybrick.target_price or 0) * mybrick.quantity
        total_sold_price += float(mybrick.total_sold_price or 0)

    today = datetime.utcnow().date()
    exists = Dashboard.objects.filter(user=user, target_at=today)
    if exists.count() > 0:
        dashboard = exists[0]
    else:
        dashboard = Dashboard()

    dashboard.user = user
    dashboard.item_count = len(mybricks)
    dashboard.item_quantity = item_quantity
    dashboard.sold_quantity = sold_quantity
    dashboard.total_buying_price = total_buying_price
    dashboard.total_estimated_price = total_estimated_price
    dashboard.total_profit = total_profit
    dashboard.total_official_price = total_official_price
    dashboard.total_target_price = total_target_price
    dashboard.total_sold_price = total_sold_price
    dashboard.target_at = today
    dashboard.bookmarked_item_count = user.bookmark_set.count()
    dashboard.save()
    logger.info("SAVE DASHBOARD: %s" % user.username)
    return dashboard
