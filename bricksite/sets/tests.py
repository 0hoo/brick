from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User

from .models import BrickSet, BricklinkRecord, EbayRecord, EbayEntry
from .utils import update_record_from_ebay


class BrickSetTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(brick_code=1, title='Test Product', official_price=10.0)
        self.brickset = BrickSet.objects.get(brick_code=1)

    def test_last_history(self):
        self.assertIsNone(self.brickset.last_bricklink_record())
        self.assertIsNone(self.brickset.last_ebay_record())

        BricklinkRecord.objects.create(brickset=self.brickset)
        EbayRecord.objects.create(brickset=self.brickset)

        self.assertIsNotNone(self.brickset.last_bricklink_record())
        self.assertIsNotNone(self.brickset.last_ebay_record())


class EbayRecordTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(brick_code=1, title='Test Product', official_price=10.0)
        self.brickset = BrickSet.objects.get(brick_code=1)

    def test_update_record_from_ebay_make_no_record(self):
        self.assertEqual(EbayRecord.objects.count(), 0)
        update_record_from_ebay()
        self.assertEqual(EbayRecord.objects.count(), 0)

    def test_update_record_from_ebay_update_record(self):
        self.assertEqual(EbayRecord.objects.count(), 0)
        EbayEntry.objects.create(brickset=self.brickset, used=False, price=15.0)
        update_record_from_ebay()
        self.assertEqual(EbayRecord.objects.count(), 1)
        history = EbayRecord.objects.latest()
        self.assertEqual(history.new_min_price, self.brickset.official_price)
        self.assertEqual(history.new_max_price, 15.0)
        self.assertEqual(history.new_average_price, 15.0)
        self.assertEqual(history.used_min_price, self.brickset.official_price)
        self.assertEqual(history.used_max_price, 0)
        self.assertEqual(history.used_average_price, 0)

        EbayEntry.objects.create(brickset=self.brickset, used=False, price=20.0)
        update_record_from_ebay()
        history = EbayRecord.objects.latest()
        self.assertEqual(EbayRecord.objects.count(), 1)
        self.assertEqual(history.new_min_price, self.brickset.official_price)
        self.assertEqual(history.new_max_price, 20.0)
        self.assertEqual(history.new_average_price, (15.0 + 20.0) / 2.0)

        EbayEntry.objects.create(brickset=self.brickset, used=True, price=11.0)
        update_record_from_ebay()
        history = EbayRecord.objects.latest()
        self.assertEqual(EbayRecord.objects.count(), 1)
        self.assertEqual(history.used_min_price, self.brickset.official_price)
        self.assertEqual(history.used_max_price, 11.0)
        self.assertEqual(history.used_average_price, 11.0)

    def test_update_history_from_ebay_ignore_big_diff(self):
        self.assertEqual(EbayRecord.objects.count(), 0)
        price = (self.brickset.official_price / Decimal(5.0)) - Decimal(1.0)
        EbayEntry.objects.create(brickset=self.brickset, used=True, price=price)
        price = (self.brickset.official_price / Decimal(3.0)) - Decimal(1.0)
        EbayEntry.objects.create(brickset=self.brickset, used=False, price=price)
        update_record_from_ebay()
        self.assertEqual(EbayRecord.objects.count(), 0)
        self.assertEqual(EbayEntry.objects.count(), 0)
