from decimal import Decimal
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from .models import MyBrick, Thing, MyBrickRecord
from .utils import update_item_record

from sets.models import BrickSet, BricklinkRecord, EbayRecord


class ItemTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(brick_code=1, title='Test Product', official_price=10.0)
        self.product = BrickSet.objects.get(brick_code=1)

    def test_buying_price_with_no_things(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        self.assertEqual(item.quantity, 0)
        self.assertEqual(item.total_buying_price, None)
        self.assertEqual(item.average_buying_price, None)
        self.assertEqual(item.estimated_total_buying_price, 0)

    def test_buying_price_with_things(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        Thing.objects.create(item=item, buying_price=15.0)
        Thing.objects.create(item=item, buying_price=18.0)
        Thing.objects.create(item=item, buying_price=14.0)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.total_buying_price, 15.0 + 18.0 + 14.0)
        self.assertEqual(item.estimated_total_buying_price, item.total_buying_price)
        self.assertEqual(item.average_buying_price, float(item.total_buying_price) / 3.0)

        Thing.objects.create(item=item)
        self.assertEqual(item.quantity, 4)
        self.assertEqual(item.total_buying_price, 15.0 + 18.0 + 14.0)
        self.assertEqual(item.average_buying_price, float(item.total_buying_price) / 3.0)
        self.assertNotEqual(item.estimated_total_buying_price, item.total_buying_price)
        self.assertEqual(item.estimated_total_buying_price, item.total_buying_price + self.product.official_price)

    def test_total_estimated_with_bricklink_history_no_things(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        BricklinkRecord.objects.create(product=self.product, new_average_price=99.0)
        self.assertEqual(item.total_estimated, 0, "Estimated value of item which have no things is zero")

    def test_total_estimated_with_opened_things(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        BricklinkRecord.objects.create(product=self.product, new_average_price=22.0, used_average_price=16.0)
        self.assertEqual(item.total_estimated, 22.0 + 16.0)

    def test_total_estimated_with_ebay_history(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        EbayRecord.objects.create(product=self.product, new_average_price=20.0, used_average_price=15.5)
        self.assertEqual(item.total_estimated, 20.0 + 15.5)

    def test_total_estimated_with_bricklink_new_ebay_used(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        BricklinkRecord.objects.create(product=self.product, new_average_price=22.0)
        EbayRecord.objects.create(product=self.product, used_average_price=15.5)
        self.assertEqual(item.total_estimated, 22.0 + 15.5)

    def test_total_estimated_with_official_price_if_history_missing(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        self.assertEqual(item.total_estimated, self.product.official_price * item.quantity)

        record = EbayRecord.objects.create(product=self.product, used_average_price=Decimal(15.5))
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        self.assertEqual(item.total_estimated, self.product.official_price + record.used_average_price)

        record.delete()
        self.assertEqual(item.total_estimated, self.product.official_price + self.product.official_price)

    def test_estimated_profit(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        Thing.objects.create(item=item, buying_price=15.0, opened=False)
        Thing.objects.create(item=item, opened=True)

        BricklinkRecord.objects.create(product=self.product, new_average_price=22.0)
        EbayRecord.objects.create(product=self.product, used_average_price=15.5)

        self.assertEqual(item.total_estimated, 22.0 + 15.5)
        self.assertEqual(item.total_buying_price, 15.0)
        self.assertEqual(item.estimated_total_buying_price, 15.0 + float(self.product.official_price))
        self.assertEqual(item.estimated_profit, item.total_estimated - item.estimated_total_buying_price)

        
class ItemRecordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(brick_code=1, title='Test Product', official_price=10.0)
        self.product = BrickSet.objects.get(brick_code=1)

    def test_update_item_record_make_no_record(self):
        self.assertEqual(MyBrickRecord.objects.count(), 0)
        update_item_record(self.user)
        self.assertEqual(MyBrickRecord.objects.count(), 0)

    def test_update_item_record_make_update_record(self):
        self.assertEqual(MyBrickRecord.objects.count(), 0)
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=False)
        update_item_record(self.user)
        self.assertEqual(MyBrickRecord.objects.count(), 1)
        record = MyBrickRecord.objects.latest()
        self.assertEqual(record.created.date(), datetime.utcnow().date())
        self.assertEqual(record.quantity, 2)
        self.assertEqual(record.estimated_price, item.total_estimated)
        self.assertEqual(record.estimated_profit, item.estimated_profit)

        BricklinkRecord.objects.create(product=self.product, new_average_price=16.0)
        update_item_record(self.user)
        self.assertEqual(MyBrickRecord.objects.count(), 1)
        record = MyBrickRecord.objects.latest()
        self.assertEqual(record.created.date(), datetime.utcnow().date())
        self.assertEqual(record.estimated_price, 16 * 2.0)

    def test_update_item_record_opened_quantity(self):
        MyBrick.objects.create(product=self.product, user=self.user)
        item = MyBrick.objects.get(product=self.product)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        Thing.objects.create(item=item, opened=True)

        update_item_record(self.user)

        history = MyBrickRecord.objects.latest()
        self.assertEqual(history.quantity, 3)
        self.assertEqual(history.opened_quantity, 2)