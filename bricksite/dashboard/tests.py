from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from .utils import snapshot_latest_dashboard

from .models import Dashboard

from sets.models import Product, BricklinkRecord, EbayRecord
from items.models import Item, Thing


class DashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        Product.objects.create(product_code=1, title='Test Product', official_price=10.0)
        self.product = Product.objects.get(product_code=1)

    def test_snapshot_last_dashboard_with_no_items(self):
        dashboard = snapshot_latest_dashboard(self.user)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertIsNotNone(dashboard)
        self.assertEqual(dashboard.user, self.user)
        self.assertEqual(dashboard.item_count, 0)
        self.assertEqual(dashboard.item_quantity, 0)
        self.assertEqual(dashboard.total_buying_price, 0)
        self.assertEqual(dashboard.total_estimated_price, 0)
        self.assertEqual(dashboard.total_profit, 0)
        self.assertEqual(dashboard.total_official_price, 0)
        self.assertEqual(dashboard.total_target_price, 0)
        self.assertEqual(dashboard.target_at, datetime.utcnow().date())

    def test_snapshot_last_dashboard_make_one_per_day(self):
        dashboard = snapshot_latest_dashboard(self.user)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertEqual(dashboard.target_at, datetime.utcnow().date())

        dashboard = snapshot_latest_dashboard(self.user)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertEqual(dashboard.target_at, datetime.utcnow().date())

    def test_snapshot_last_dashboard_values(self):
        Item.objects.create(product=self.product, user=self.user)
        item = Item.objects.get(product=self.product)
        Thing.objects.create(item=item, buying_price=8.0)
        Thing.objects.create(item=item, buying_price=9.0)

        dashboard = snapshot_latest_dashboard(self.user)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertEqual(dashboard.item_count, 1)
        self.assertEqual(dashboard.item_quantity, 2)
        self.assertEqual(dashboard.total_buying_price, 8.0 + 9.0)
        self.assertEqual(dashboard.total_estimated_price, 20)
        self.assertEqual(dashboard.total_official_price, 20)
        self.assertEqual(dashboard.total_profit, float(dashboard.total_estimated_price) - dashboard.total_buying_price)

        BricklinkRecord.objects.create(product=self.product, new_average_price=15.0)
        EbayRecord.objects.create(product=self.product, used_average_price=12.5)
        Thing.objects.create(item=item, buying_price=7.0, opened=True)

        dashboard = snapshot_latest_dashboard(self.user)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertEqual(dashboard.item_count, 1)
        self.assertEqual(dashboard.item_quantity, 3)
        self.assertEqual(dashboard.total_buying_price, 8.0 + 9.0 + 7.0)
        self.assertEqual(dashboard.total_estimated_price, 15.0 * 2 + 12.5)
        self.assertEqual(dashboard.total_official_price, 30)
        self.assertEqual(dashboard.total_profit, float(dashboard.total_estimated_price) - dashboard.total_buying_price)
