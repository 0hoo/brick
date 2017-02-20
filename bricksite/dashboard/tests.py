from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from .utils import snapshot_latest_dashboard

from .models import Dashboard

from sets.models import BrickSet, BricklinkRecord, EbayRecord
from mybricks.models import MyBrick, MyBrickItem


class DashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(brick_code=1, title='Test Product', official_price=10.0)
        self.brickset = BrickSet.objects.get(brick_code=1)

    def test_snapshot_last_dashboard_with_no_items(self):
        dashboard = snapshot_latest_dashboard(self.user)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertIsNotNone(dashboard)
        self.assertEqual(dashboard.user, self.user)
        self.assertEqual(dashboard.mybrick_count, 0)
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
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=8.0)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=9.0)

        dashboard = snapshot_latest_dashboard(self.user)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertEqual(dashboard.mybrick_count, 1)
        self.assertEqual(dashboard.item_quantity, 2)
        self.assertEqual(dashboard.total_buying_price, 8.0 + 9.0)
        self.assertEqual(dashboard.total_estimated_price, 20)
        self.assertEqual(dashboard.total_official_price, 20)
        self.assertEqual(dashboard.total_profit, float(dashboard.total_estimated_price) - dashboard.total_buying_price)

        BricklinkRecord.objects.create(brickset=self.brickset, new_average_price=15.0)
        EbayRecord.objects.create(brickset=self.brickset, used_average_price=12.5)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=7.0, opened=True)

        dashboard = snapshot_latest_dashboard(self.user)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertEqual(dashboard.mybrick_count, 1)
        self.assertEqual(dashboard.item_quantity, 3)
        self.assertEqual(dashboard.total_buying_price, 8.0 + 9.0 + 7.0)
        self.assertEqual(dashboard.total_estimated_price, 15.0 * 2 + 12.5)
        self.assertEqual(dashboard.total_official_price, 30)
        self.assertEqual(dashboard.total_profit, float(dashboard.total_estimated_price) - dashboard.total_buying_price)
