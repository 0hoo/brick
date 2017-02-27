from decimal import Decimal
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import MyBrick, MyBrickItem, MyBrickRecord
from .utils import update_mybrick_record

from sets.models import BrickSet, BricklinkRecord, EbayRecord


class MyBricksViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        self.client.login(username='tmb', password='tmb')

    def test_list_with_no_mybricks(self):
        response = self.client.get(reverse('mybricks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['mybricks'], [])
        self.assertTemplateUsed(response, 'mybricks/list.html')

    def test_list_with_bricks(self):
        set1 = BrickSet.objects.create(brick_code=1, title='Set1', official_price=10.0, is_approved=True)
        set2 = BrickSet.objects.create(brick_code=2, title='Set2', official_price=10.0, is_approved=True)

        response = self.client.get(reverse('mybricks:list'))
        self.assertQuerysetEqual(response.context['mybricks'], [])

        mybrick1 = MyBrick.objects.create(brickset=set1, user=self.user)
        mybrick2 = MyBrick.objects.create(brickset=set2, user=self.user)

        response = self.client.get(reverse('mybricks:list'))
        self.assertQuerysetEqual(response.context['mybricks'], [repr(mybrick2), repr(mybrick1)])

    def test_list_theme_titles(self):
        response = self.client.get(reverse('mybricks:list'))
        self.assertEqual(len(response.context['theme_titles']), 0)

        set1 = BrickSet.objects.create(brick_code=1, title='Set1', official_price=10.0, is_approved=True, theme_title='A')
        set2 = BrickSet.objects.create(brick_code=2, title='Set2', official_price=10.0, is_approved=True, theme_title='B')
        MyBrick.objects.create(brickset=set1, user=self.user)
        MyBrick.objects.create(brickset=set2, user=self.user)

        response = self.client.get(reverse('mybricks:list'))
        self.assertQuerysetEqual(response.context['theme_titles'], ["'A'", "'B'"])
        self.assertEqual(response.context['theme_title'], None)
        self.assertEqual(len(response.context['mybricks']), 2)

        response = self.client.get(reverse('mybricks:list_by_theme', kwargs={'theme_title': 'B'}))
        self.assertEqual(response.context['theme_title'], 'B')
        self.assertEqual(len(response.context['mybricks']), 1)

    def test_list_unapproved(self):
        set1 = BrickSet.objects.create(brick_code=1, title='Set1', official_price=10.0, is_approved=True)
        set2 = BrickSet.objects.create(brick_code=2, title='Set2', official_price=10.0, is_approved=False)
        MyBrick.objects.create(brickset=set1, user=self.user)
        MyBrick.objects.create(brickset=set2, user=self.user)

        response = self.client.get(reverse('mybricks:list'))
        self.assertEqual(len(response.context['mybricks']), 1)


class MyBrickDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        self.client.login(username='tmb', password='tmb')

        self.set1 = BrickSet.objects.create(brick_code=1, title='Set1', official_price=10.0, is_approved=True)

    def test_detail_404(self):
        response = self.client.get(reverse('mybricks:detail', kwargs={'brick_code': self.set1.brick_code }))
        self.assertEqual(response.status_code, 404)

    def test_detail_200(self):
        mybrick = MyBrick.objects.create(brickset=self.set1, user=self.user)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=11.0, opened=False)

        response = self.client.get(reverse('mybricks:detail', kwargs={'brick_code': mybrick.brickset.brick_code }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repr(response.context['mybrick']), repr(mybrick))
        self.assertTemplateUsed(response, 'mybricks/detail.html')

    def test_detail_item(self):
        mybrick = MyBrick.objects.create(brickset=self.set1, user=self.user)
        item = MyBrickItem.objects.create(mybrick=mybrick, buying_price=11.0, opened=False)

        response = self.client.get(reverse('mybricks:detail', kwargs={'brick_code': mybrick.brickset.brick_code }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<span class="ui circular label">1</span>')
        self.assertContains(response, '<strong>unopened</strong>')
        self.assertContains(response, ' item of this brick.')

        item.opened = True
        item.save()

        response = self.client.get(reverse('mybricks:detail', kwargs={'brick_code': mybrick.brickset.brick_code}))
        self.assertContains(response, '<span class="ui circular label">1</span>')
        self.assertNotContains(response, '<strong>unopened</strong>')
        self.assertContains(response, '<strong>opened</strong>')

    def test_detail_items(self):
        mybrick = MyBrick.objects.create(brickset=self.set1, user=self.user)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=11.0, opened=False)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=9.0, opened=True)

        response = self.client.get(reverse('mybricks:detail', kwargs={'brick_code': mybrick.brickset.brick_code }))
        self.assertContains(response, '<strong>2</strong>')
        self.assertContains(response, ' items of this brick.')
        self.assertContains(response, '<div class="ui list">')


class MyBrickTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(brick_code=1, title='Test Set', official_price=10.0)
        self.brickset = BrickSet.objects.get(brick_code=1)

    def test_buying_price_with_no_items(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        self.assertEqual(mybrick.quantity, 0)
        self.assertEqual(mybrick.total_buying_price, None)
        self.assertEqual(mybrick.average_buying_price, None)
        self.assertEqual(mybrick.estimated_total_buying_price, 0)

    def test_order_of_items(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        item1 = MyBrickItem.objects.create(mybrick=mybrick, buying_price=10.0)
        item1 = MyBrickItem.objects.get(id=item1.id)
        item2 = MyBrickItem.objects.create(mybrick=mybrick, buying_price=12.0)
        item2 = MyBrickItem.objects.get(id=item2.id)
        item3 = MyBrickItem.objects.create(mybrick=mybrick, buying_price=7.0, opened=True)
        item3 = MyBrickItem.objects.get(id=item3.id)
        item4 = MyBrickItem.objects.create(mybrick=mybrick, buying_price=12.0)
        item4 = MyBrickItem.objects.get(id=item4.id)

        self.assertQuerysetEqual(mybrick.item_set.all(), [repr(item1), repr(item2), repr(item3), repr(item4)])

        item1.sold = True
        item1.save()
        self.assertQuerysetEqual(mybrick.item_set.all(), [repr(item2), repr(item3), repr(item4), repr(item1)])

    def test_buying_price_with_items(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=15.0)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=18.0)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=14.0)
        self.assertEqual(mybrick.quantity, 3)
        self.assertEqual(mybrick.total_buying_price, 15.0 + 18.0 + 14.0)
        self.assertEqual(mybrick.estimated_total_buying_price, mybrick.total_buying_price)
        self.assertEqual(mybrick.average_buying_price, float(mybrick.total_buying_price) / 3.0)

        MyBrickItem.objects.create(mybrick=mybrick)
        self.assertEqual(mybrick.quantity, 4)
        self.assertEqual(mybrick.total_buying_price, 15.0 + 18.0 + 14.0)
        self.assertEqual(mybrick.average_buying_price, float(mybrick.total_buying_price) / 3.0)
        self.assertNotEqual(mybrick.estimated_total_buying_price, mybrick.total_buying_price)
        self.assertEqual(mybrick.estimated_total_buying_price, mybrick.total_buying_price + self.brickset.official_price)

    def test_total_estimated_with_bricklink_history_no_items(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        BricklinkRecord.objects.create(brickset=self.brickset, new_average_price=99.0)
        self.assertEqual(mybrick.total_estimated, 0, "Estimated value of item which have no things is zero")

    def test_total_estimated_with_opened_items(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        MyBrickItem.objects.create(mybrick=mybrick, opened=False)
        MyBrickItem.objects.create(mybrick=mybrick, opened=True)
        BricklinkRecord.objects.create(brickset=self.brickset, new_average_price=22.0, used_average_price=16.0)
        self.assertEqual(mybrick.total_estimated, 22.0 + 16.0)

    def test_total_estimated_with_ebay_record(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        MyBrickItem.objects.create(mybrick=mybrick, opened=False)
        MyBrickItem.objects.create(mybrick=mybrick, opened=True)
        EbayRecord.objects.create(brickset=self.brickset, new_average_price=20.0, used_average_price=15.5)
        self.assertEqual(mybrick.total_estimated, 20.0 + 15.5)

    def test_total_estimated_with_bricklink_new_ebay_used(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        MyBrickItem.objects.create(mybrick=mybrick, opened=False)
        MyBrickItem.objects.create(mybrick=mybrick, opened=True)
        BricklinkRecord.objects.create(brickset=self.brickset, new_average_price=22.0)
        EbayRecord.objects.create(brickset=self.brickset, used_average_price=15.5)
        self.assertEqual(mybrick.total_estimated, 22.0 + 15.5)

    def test_total_estimated_with_official_price_if_record_missing(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        self.assertEqual(mybrick.total_estimated, self.brickset.official_price * mybrick.quantity)

        record = EbayRecord.objects.create(brickset=self.brickset, used_average_price=Decimal(15.5))
        MyBrickItem.objects.create(mybrick=mybrick, opened=False)
        MyBrickItem.objects.create(mybrick=mybrick, opened=True)
        self.assertEqual(mybrick.total_estimated, self.brickset.official_price + record.used_average_price)

        record.delete()
        self.assertEqual(mybrick.total_estimated, self.brickset.official_price + self.brickset.official_price)

    def test_estimated_profit(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        MyBrickItem.objects.create(mybrick=mybrick, buying_price=15.0, opened=False)
        MyBrickItem.objects.create(mybrick=mybrick, opened=True)

        BricklinkRecord.objects.create(brickset=self.brickset, new_average_price=22.0)
        EbayRecord.objects.create(brickset=self.brickset, used_average_price=15.5)

        self.assertEqual(mybrick.total_estimated, 22.0 + 15.5)
        self.assertEqual(mybrick.total_buying_price, 15.0)
        self.assertEqual(mybrick.estimated_total_buying_price, 15.0 + float(self.brickset.official_price))
        self.assertEqual(mybrick.estimated_profit, mybrick.total_estimated - mybrick.estimated_total_buying_price)

        
class MyBrickRecordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        BrickSet.objects.create(brick_code=1, title='Test Set', official_price=10.0)
        self.brickset = BrickSet.objects.get(brick_code=1)

    def test_update_item_record_make_no_record(self):
        self.assertEqual(MyBrickRecord.objects.count(), 0)
        update_mybrick_record(self.user)
        self.assertEqual(MyBrickRecord.objects.count(), 0)

    def test_update_item_record_make_update_record(self):
        self.assertEqual(MyBrickRecord.objects.count(), 0)
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        MyBrickItem.objects.create(mybrick=mybrick, opened=False)
        MyBrickItem.objects.create(mybrick=mybrick, opened=False)
        update_mybrick_record(self.user)
        self.assertEqual(MyBrickRecord.objects.count(), 1)
        record = MyBrickRecord.objects.latest()
        self.assertEqual(record.created.date(), datetime.utcnow().date())
        self.assertEqual(record.quantity, 2)
        self.assertEqual(record.estimated_price, mybrick.total_estimated)
        self.assertEqual(record.estimated_profit, mybrick.estimated_profit)

        BricklinkRecord.objects.create(brickset=self.brickset, new_average_price=16.0)
        update_mybrick_record(self.user)
        self.assertEqual(MyBrickRecord.objects.count(), 1)
        record = MyBrickRecord.objects.latest()
        self.assertEqual(record.created.date(), datetime.utcnow().date())
        self.assertEqual(record.estimated_price, 16 * 2.0)

    def test_update_item_record_opened_quantity(self):
        MyBrick.objects.create(brickset=self.brickset, user=self.user)
        mybrick = MyBrick.objects.get(brickset=self.brickset)
        MyBrickItem.objects.create(mybrick=mybrick, opened=False)
        MyBrickItem.objects.create(mybrick=mybrick, opened=True)
        MyBrickItem.objects.create(mybrick=mybrick, opened=True)

        update_mybrick_record(self.user)

        history = MyBrickRecord.objects.latest()
        self.assertEqual(history.quantity, 3)
        self.assertEqual(history.opened_quantity, 2)
