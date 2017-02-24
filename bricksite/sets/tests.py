from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import BrickSet, BricklinkRecord, EbayRecord, EbayEntry
from .utils import update_record_from_ebay


class BrickSetsTests(TestCase):
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


class BrickSetsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tmb', email='tmb@trackmybrick.com', password='tmb')
        self.client.login(username='tmb', password='tmb')

    def test_list_with_no_bricksets(self):
        response = self.client.get(reverse('sets:list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['bricksets'], [])
        self.assertTemplateUsed(response, 'sets/list.html')

    def test_list_with_bricksets(self):
        brickset = BrickSet.objects.create(brick_code=1, title='Test Set', official_price=10.0, is_approved=True)
        response = self.client.get(reverse('sets:list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['bricksets'], [repr(brickset)])
        self.assertTemplateUsed(response, 'sets/list.html')

    def test_list_contain_detail_url(self):
        brickset = BrickSet.objects.create(brick_code=1, title='Test Set', official_price=10.0, is_approved=True)
        response = self.client.get(reverse('sets:list'))
        detail_url = reverse('sets:detail', args=[str(brickset.brick_code)])
        self.assertContains(response, detail_url)

    def test_list_with_unapproved(self):
        approved = BrickSet.objects.create(brick_code=1, title='Test Set', official_price=10.0, is_approved=True)
        BrickSet.objects.create(brick_code=2, title='Unknown Set', is_approved=False)
        response = self.client.get(reverse('sets:list'))
        self.assertQuerysetEqual(response.context['bricksets'], [repr(approved)])
        self.assertEqual(len(response.context['bricksets']), 1)

    def test_list_theme_titles(self):
        BrickSet.objects.create(brick_code=1, title='Set1', official_price=10.0, is_approved=True, theme_title='A')
        BrickSet.objects.create(brick_code=2, title='Set2', official_price=10.0, is_approved=True, theme_title='B')
        response = self.client.get(reverse('sets:list'))
        self.assertEqual(response.context['theme_title'], None)
        self.assertQuerysetEqual(response.context['theme_titles'], ["'A'", "'B'"])
        self.assertEqual(len(response.context['bricksets']), 2)

    def test_list_theme_title(self):
        BrickSet.objects.create(brick_code=1, title='Set1', official_price=10.0, is_approved=True, theme_title='A')
        themeb_set = BrickSet.objects.create(brick_code=2, title='Set2', official_price=10.0, is_approved=True, theme_title='B')
        response = self.client.get(reverse('sets:list_by_theme', kwargs={'theme_title': 'B'}))
        self.assertEqual(response.context['theme_title'], 'B')
        self.assertQuerysetEqual(response.context['theme_titles'], ["'A'", "'B'"])
        self.assertEqual(len(response.context['bricksets']), 1)
        self.assertQuerysetEqual(response.context['bricksets'], [repr(themeb_set)])

    def test_list_theme_titles_of_unapproved(self):
        BrickSet.objects.create(brick_code=1, title='Set1', official_price=10.0, is_approved=True, theme_title='A')
        BrickSet.objects.create(brick_code=2, title='Set2', official_price=10.0, is_approved=True, theme_title='B')
        BrickSet.objects.create(brick_code=3, title='Set3', official_price=10.0, is_approved=False, theme_title='B')
        BrickSet.objects.create(brick_code=4, title='Set4', official_price=10.0, is_approved=False, theme_title='C')
        response = self.client.get(reverse('sets:list'))
        self.assertEqual(response.context['theme_title'], None)
        self.assertQuerysetEqual(response.context['theme_titles'], ["'A'", "'B'"])
        self.assertEqual(len(response.context['bricksets']), 2)

    def test_list_order_by_price(self):
        set1 = BrickSet.objects.create(brick_code=1, title='Set1', official_price=10.0, is_approved=True)
        set2 = BrickSet.objects.create(brick_code=2, title='Set2', official_price=20.0, is_approved=True)
        set3 = BrickSet.objects.create(brick_code=3, title='Set3', official_price=15.0, is_approved=True)
        response = self.client.get(reverse('sets:list'))
        self.assertQuerysetEqual(response.context['bricksets'], [repr(set2), repr(set3), repr(set1)])


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
