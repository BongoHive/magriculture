from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import FarmerGroup, Farmer
from datetime import datetime


def create_farmer_for_agent(agent, market, **kwargs):
	farmer = utils.create_farmer(**kwargs)
	farmer.operates_at(market, agent)
	return farmer

def create_random_farmers(amount, agent, market):
	for i in range(amount):
		yield create_farmer_for_agent(agent, market, msisdn=27761234567 + i)

class FNCSTestCase(TestCase):

	def setUp(self):
		self.client = Client()
		self.pin = '1234'
		self.province = utils.create_province('test province')
		self.district = utils.create_district('test district', self.province)
		self.market = utils.create_market('test market', self.district)
		self.agent = utils.create_agent(password='1234')
		self.msisdn = self.agent.actor.user.username
		self.login_url = '%s?next=%s' % (reverse('login'), reverse('fncs:home'))
		self.farmers = list(create_random_farmers(10, self.agent, self.market))
		self.farmer = self.farmers[0]
		self.farmergroup = self.farmer.farmergroup

	def login(self):
		self.client.login(username=self.msisdn, password=self.pin)

	def logout(self):
		self.client.logout()

class SessionTestCase(FNCSTestCase):

	def tearDown(self):
		pass

	def test_redirect_for_login(self):
		response = self.client.get(reverse('fncs:home'))
		self.assertRedirects(response, self.login_url)

	def test_login(self):
		self.login()
		response = self.client.get(reverse('fncs:home'))
		self.assertEqual(response.status_code, 200)

	def test_logout_redirect(self):
		self.login()
		response = self.client.get(reverse('logout'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'logged out')
		response = self.client.get(reverse('fncs:home'))
		self.assertRedirects(response, self.login_url)

def format_timestamp(key, timestamp):
	return {
		'%s_0_year' % key: timestamp.year,
		'%s_0_month' % key: timestamp.month,
		'%s_0_day' % key: timestamp.day,
		'%s_1_hour' % key: timestamp.hour,
		'%s_1_minute' % key: timestamp.minute,
	}

class FarmersTestCase(FNCSTestCase):

	def setUp(self):
		super(FarmersTestCase, self).setUp()
		self.test_msisdn = '27861234567'
		self.login()

	def farmer_url(self, *args, **kwargs):
		return utils.farmer_url(self.farmer.pk, *args, **kwargs)

	def take_in(self, *args):
		return utils.take_in(self.market, self.agent, self.farmer, *args)

	def test_farmer_listing(self):
		response = self.client.get(reverse('fncs:farmers'))
		self.assertEqual(response.status_code, 200)

	def test_farmer_querying(self):
		response = self.client.get(reverse('fncs:farmers'), {
			'q': 'xyz'
		})
		self.assertContains(response, 'No farmers match')
		response = self.client.get(reverse('fncs:farmers'), {
			'q': unicode(self.farmers[0])
		})
		self.assertNotContains(response, 'No farmers match')

	def test_farmer_creation(self):
		self.assertFalse(utils.is_farmer(self.test_msisdn))
		response = self.client.get(reverse('fncs:farmer_new'))
		self.assertEqual(response.status_code, 200)
		response = self.client.post(reverse('fncs:farmer_new'), {
			'msisdn': self.test_msisdn,
			'name': 'name',
			'surname': 'surname',
			'farmergroup': self.farmergroup.pk,
			'markets': [self.market.pk],
		})
		self.assertTrue(utils.is_farmer(self.test_msisdn))

	def test_farmer_view(self):
		response = self.client.get(self.farmer_url())
		self.assertRedirects(response, self.farmer_url('sales'))

	def test_farmer_sale(self):
		receipt = self.take_in(10, 'boxes', 'tomato')
		sale = utils.sell(receipt, 10, 10)
		response = self.client.get(self.farmer_url('sale', sale_pk=sale.pk))
		self.assertContains(response, '10 boxes of tomato', status_code=200)

	def test_farmer_new_sale(self):
		# create sample crop data
		crop_names = ["onion", "potato", "apple"]
		other_crops = [utils.create_crop(crop_name) for crop_name in crop_names]

		receipt = self.take_in(10, 'boxes', 'tomato')
		response = self.client.get(self.farmer_url('new_sale'))
		self.assertContains(response, 'tomato')
		crop_receipts = self.agent.cropreceipts_available_for(self.farmer)
		crop_inventory = [cr.crop for cr in crop_receipts]
		for crop in other_crops:
			self.assertNotIn(crop, crop_inventory)
			self.assertNotContains(response, crop.name)

	def test_farmer_new_sale_detail(self):
		receipt = self.take_in(10, 'boxes', 'tomato')
		self.assertFalse(receipt.reconciled)
		sale_url = '%s?crop_receipt=%s' % (self.farmer_url('new_sale_detail'),
			receipt.pk)
		response = self.client.get(sale_url)
		self.assertEqual(response.status_code, 200)
		response = self.client.post(sale_url, {
			'cancel': 1,
		}, follow=True)
		self.assertEqual(response.redirect_chain, [
			('http://testserver%s' % self.farmer_url(), 302),
			('http://testserver%s' % self.farmer_url('sales'), 302),
		])
		# self.assertRedirects(response, status_code=200, self.farmer_url('sales'))
		post_args = format_timestamp('created_at', datetime.now())
		post_args.update({
			'crop_receipt': receipt.pk,
			'price': 10.0,
			'amount': receipt.amount,
			'market': self.market.pk,
		})
		response = self.client.post(sale_url, post_args, follow=True)
		self.assertRedirects(response, self.farmer_url('sales'))
		transaction = receipt.farmer.transactions().latest()
		self.assertEqual(transaction.crop_receipt.pk, receipt.pk)
		self.assertEqual(transaction.price, 10)
		self.assertEqual(transaction.amount, receipt.amount)
		self.assertEqual(transaction.total, 10 * receipt.amount)
		self.assertTrue(transaction.crop_receipt.reconciled)
