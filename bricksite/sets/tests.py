from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User

from .models import BrickSet, BricklinkRecord, EbayRecord, EbayItem
from .utils import update_record_from_ebay


class ProductTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(product_code=1, title='Test Product', official_price=10.0)
        self.product = BrickSet.objects.get(product_code=1)

    def test_last_history(self):
        self.assertIsNone(self.product.last_bricklink_record())
        self.assertIsNone(self.product.last_ebay_record())

        BricklinkRecord.objects.create(product=self.product)
        EbayRecord.objects.create(product=self.product)

        self.assertIsNotNone(self.product.last_bricklink_record())
        self.assertIsNotNone(self.product.last_ebay_record())


class EbayRecordTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(product_code=1, title='Test Product', official_price=10.0)
        self.product = BrickSet.objects.get(product_code=1)

    def test_update_history_from_ebay_make_no_history(self):
        self.assertEqual(EbayRecord.objects.count(), 0)
        update_record_from_ebay()
        self.assertEqual(EbayRecord.objects.count(), 0)

    def test_update_history_from_ebay_update_history(self):
        self.assertEqual(EbayRecord.objects.count(), 0)
        EbayItem.objects.create(product=self.product, used=False, price=15.0)
        update_record_from_ebay()
        self.assertEqual(EbayRecord.objects.count(), 1)
        history = EbayRecord.objects.latest()
        self.assertEqual(history.new_min_price, self.product.official_price)
        self.assertEqual(history.new_max_price, 15.0)
        self.assertEqual(history.new_average_price, 15.0)
        self.assertEqual(history.used_min_price, self.product.official_price)
        self.assertEqual(history.used_max_price, 0)
        self.assertEqual(history.used_average_price, 0)

        EbayItem.objects.create(product=self.product, used=False, price=20.0)
        update_record_from_ebay()
        history = EbayRecord.objects.latest()
        self.assertEqual(EbayRecord.objects.count(), 1)
        self.assertEqual(history.new_min_price, self.product.official_price)
        self.assertEqual(history.new_max_price, 20.0)
        self.assertEqual(history.new_average_price, (15.0 + 20.0) / 2.0)

        EbayItem.objects.create(product=self.product,used=True, price=11.0)
        update_record_from_ebay()
        history = EbayRecord.objects.latest()
        self.assertEqual(EbayRecord.objects.count(), 1)
        self.assertEqual(history.used_min_price, self.product.official_price)
        self.assertEqual(history.used_max_price, 11.0)
        self.assertEqual(history.used_average_price, 11.0)

    def test_update_history_from_ebay_ignore_big_diff(self):
        self.assertEqual(EbayRecord.objects.count(), 0)
        price = (self.product.official_price / Decimal(5.0)) - Decimal(1.0)
        EbayItem.objects.create(product=self.product, used=True, price=price)
        price = (self.product.official_price / Decimal(3.0)) - Decimal(1.0)
        EbayItem.objects.create(product=self.product, used=False, price=price)
        update_record_from_ebay()
        self.assertEqual(EbayRecord.objects.count(), 0)
        self.assertEqual(EbayItem.objects.count(), 0)
