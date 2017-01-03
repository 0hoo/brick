from decimal import Decimal
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Item, Thing, ItemRecord
from .utils import update_item_record

from products.models import Product, BricklinkRecord, EbayRecord


class ItemTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        Product.objects.create(product_code=1, title='Test Product', official_price=10.0)
        self.product = Product.objects.get(product_code=1)

    def test_total_buying_price_with_no_things(self):
        Item.objects.create(product=self.product, user=self.user, buying_price=12.0, quantity=1)
        item = Item.objects.get(product=self.product)
        self.assertEqual(item.total_buying_price, 12.0)

        item.quantity = 3
        self.assertEqual(item.total_buying_price, 12.0 * 3)

    def test_total_buying_price_with_no_things_no_buying_price(self):
        Item.objects.create(product=self.product, user=self.user, quantity=2)
        item = Item.objects.get(product=self.product)
        self.assertEqual(item.total_buying_price, self.product.official_price * 2)

    def test_total_buying_price_with_things(self):
        Item.objects.create(product=self.product, user=self.user, buying_price=12.0, quantity=3)
        item = Item.objects.get(product=self.product)
        Thing.objects.create(item=item, buying_price=15.0)
        Thing.objects.create(item=item, buying_price=18.0)
        Thing.objects.create(item=item, buying_price=14.0)
        self.assertEqual(item.total_buying_price, 15.0 + 18.0 + 14.0)

        item.quantity = 4
        Thing.objects.create(item=item)
        self.assertEqual(item.total_buying_price, 15.0 + 18.0 + 14.0 + 12.0)

    def test_buying_average_price(self):
        Item.objects.create(product=self.product, user=self.user, buying_price=12.0, quantity=2)
        item = Item.objects.get(product=self.product)
        Thing.objects.create(item=item, buying_price=15.0)
        Thing.objects.create(item=item, buying_price=18.0)
        self.assertEqual(item.buying_average_price, (15.0 + 18.0) / item.quantity)

    def test_total_estimated_with_bricklink_history_no_things(self):
        Item.objects.create(product=self.product, user=self.user, quantity=2)
        item = Item.objects.get(product=self.product)
        BricklinkRecord.objects.create(product=self.product, new_average_price=22.0)
        self.assertEqual(item.total_estimated, 22.0 * 2)

    def test_total_estimated_with_opened_things(self):
        Item.objects.create(product=self.product, user=self.user, quantity=2)
        item = Item.objects.get(product=self.product)
        BricklinkRecord.objects.create(product=self.product, new_average_price=22.0, used_average_price=16.0)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        self.assertEqual(item.total_estimated, 22.0 + 16.0)

    def test_total_estimated_with_ebay_history(self):
        Item.objects.create(product=self.product, user=self.user, quantity=2)
        item = Item.objects.get(product=self.product)
        EbayRecord.objects.create(product=self.product, new_average_price=20.0, used_average_price=15.5)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        self.assertEqual(item.total_estimated, 20.0 + 15.5)

    def test_total_estimated_with_bricklink_new_ebay_used(self):
        Item.objects.create(product=self.product, user=self.user, quantity=2)
        item = Item.objects.get(product=self.product)
        BricklinkRecord.objects.create(product=self.product, new_average_price=22.0)
        EbayRecord.objects.create(product=self.product, used_average_price=15.5)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        self.assertEqual(item.total_estimated, 22.0 + 15.5)

    def test_total_estimated_with_official_price_if_history_missing(self):
        Item.objects.create(product=self.product, user=self.user, quantity=2)
        item = Item.objects.get(product=self.product)
        self.assertEqual(item.total_estimated, self.product.official_price * item.quantity)

        history = EbayRecord.objects.create(product=self.product, used_average_price=Decimal(15.5))
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        self.assertEqual(item.total_estimated, self.product.official_price + history.used_average_price)

        history.delete()
        self.assertEqual(item.total_estimated, self.product.official_price + self.product.official_price)

    def test_estimated_profit(self):
        Item.objects.create(product=self.product, user=self.user, buying_price=12.0, quantity=2)
        item = Item.objects.get(product=self.product)
        Thing.objects.create(item=item, buying_price=15.0, opened=False)
        Thing.objects.create(item=item, opened=True)

        BricklinkRecord.objects.create(product=self.product, new_average_price=22.0)
        EbayRecord.objects.create(product=self.product, used_average_price=15.5)

        self.assertEqual(item.total_estimated, 22.0 + 15.5)
        self.assertEqual(item.total_buying_price, 15.0 + 12.0)
        self.assertEqual(item.estimated_profit, item.total_estimated - item.total_buying_price)
        
        
class ItemHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        Product.objects.create(product_code=1, title='Test Product', official_price=10.0)
        self.product = Product.objects.get(product_code=1)

    def test_update_item_record_make_no_history(self):
        self.assertEqual(ItemRecord.objects.count(), 0)
        update_item_record(self.user)
        self.assertEqual(ItemRecord.objects.count(), 0)

    def test_update_item_record_make_update_history(self):
        self.assertEqual(ItemRecord.objects.count(), 0)
        Item.objects.create(product=self.product, user=self.user, buying_price=9.0, quantity=2)
        item = Item.objects.get(product=self.product)
        update_item_record(self.user)
        self.assertEqual(ItemRecord.objects.count(), 1)
        history = ItemRecord.objects.latest()
        self.assertEqual(history.created.date(), datetime.utcnow().date())
        self.assertEqual(history.quantity, 2)
        self.assertEqual(history.estimated_price, item.total_estimated)
        self.assertEqual(history.estimated_profit, item.estimated_profit)

        BricklinkRecord.objects.create(product=self.product, new_average_price=16.0)
        update_item_record(self.user)
        self.assertEqual(ItemRecord.objects.count(), 1)
        history = ItemRecord.objects.latest()
        self.assertEqual(history.created.date(), datetime.utcnow().date())
        self.assertEqual(history.estimated_price, 16 * 2.0)

    def test_update_item_record_opened_quantity(self):
        Item.objects.create(product=self.product, user=self.user, buying_price=9.0, quantity=3)
        item = Item.objects.get(product=self.product)
        Thing.objects.create(item=item, opened=False)
        Thing.objects.create(item=item, opened=True)
        Thing.objects.create(item=item, opened=True)

        update_item_record(self.user)

        history = ItemRecord.objects.latest()
        self.assertEqual(history.quantity, 3)
        self.assertEqual(history.opened_quantity, 2)