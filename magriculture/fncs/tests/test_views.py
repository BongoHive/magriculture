from datetime import datetime

from django.test import TestCase
from django.test.client import Client
from django.utils.unittest import skip
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import FarmerGroup, Farmer, MarketMonitor
from magriculture.fncs.models.geo import Market


def create_farmer_for_agent(agent, market, **kwargs):
    farmer = utils.create_farmer(**kwargs)
    farmer.operates_at(market, agent)
    return farmer

def create_random_farmers(amount, agent, market):
    for i in range(amount):
        yield create_farmer_for_agent(agent, market, msisdn=27731234567 + i)

class FNCSTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.pin = '1234'
        self.province = utils.create_province('test province')
        self.district = utils.create_district('test district', self.province)
        self.market = utils.create_market('test market', self.district)

        self.agent = utils.create_agent()
        self.msisdn = self.agent.actor.user.username

        identity = self.agent.actor.get_identity(self.msisdn)
        identity.set_pin(self.pin)
        identity.save()

        self.login_url = '%s?next=%s' % (reverse('login'), reverse('fncs:home'))
        self.farmers = list(create_random_farmers(10, self.agent, self.market))
        self.farmer = self.farmers[0]
        self.farmergroup = self.farmer.farmergroup

    def farmer_url(self, *args, **kwargs):
        return utils.farmer_url(self.farmer.pk, *args, **kwargs)

    def take_in(self, *args):
        return utils.take_in(self.market, self.agent, self.farmer, *args)

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

    def test_farmer_id_number(self):
        response = self.client.post(self.farmer_url('edit'), {
            'msisdn': self.test_msisdn,
            'name': 'name',
            'surname': 'surname',
            'farmergroup': self.farmergroup.pk,
            'markets': [self.market.pk],
            'id_number': '123456789',
            })
        self.assertRedirects(response, self.farmer_url('crops'))
        farmer = Farmer.objects.get(pk=self.farmer.pk)
        self.assertEqual(farmer.id_number, '123456789')

    def test_farmer_id_number_uniqueness(self):

        # Test that we cannot create farmers with the same id number
        farmer = utils.create_farmer(msisdn='123')
        farmer.id_number = '123456789'
        farmer.save()

        # Test that we cannot create farmers with the same id number
        farmer = utils.create_farmer(msisdn='456')  # different msisdn
        farmer.id_number = '123456789'  # same id_number

        self.assertRaises(IntegrityError, farmer.save)


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
        self.assertRedirects(response, self.farmer_url('sales'))
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

    def test_farmer_profile(self):
        response = self.client.get(self.farmer_url('profile'))
        self.assertContains(response, self.farmer.actor.name)

    def test_farmer_crops(self):
        random_crops = [utils.create_crop(n) for n in
                            ['tomatoe', 'potato', 'carrot']]
        receipt1 = self.take_in(10, 'boxes', 'apple')
        receipt2 = self.take_in(20, 'kilos', 'cabbage')
        response = self.client.get(self.farmer_url('crops'))
        self.assertContains(response, receipt1.crop.name)
        self.assertContains(response, receipt2.crop.name)
        response = self.client.post(self.farmer_url('crops'), {
            'crops': [crop.pk for crop in random_crops]
        }, follow=True)
        # this should be a mass override
        for crop in random_crops:
            self.assertContains(response, crop.name)
        # previous selection should have been cleared
        self.assertNotContains(response, receipt1.crop.name)
        self.assertNotContains(response, receipt2.crop.name)
        self.assertRedirects(response, self.farmer_url('sales'))


    def test_farmer_edit(self):
        farmer_url = self.farmer_url('edit')
        response = self.client.get(farmer_url)
        user = self.farmer.actor.user
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.username)
        response = self.client.post(farmer_url, {
            'name': 'n',
            'surname': 'sn',
            'msisdn': '1',
            'farmergroup': self.farmergroup.pk,
            'markets': [self.market.pk],
        })
        self.assertRedirects(response, self.farmer_url('crops'))
        farmer = Farmer.objects.get(pk=self.farmer.pk)
        user = farmer.actor.user
        self.assertEqual(user.first_name, 'n')
        self.assertEqual(user.last_name, 'sn')
        self.assertEqual(user.username, '1')
        self.assertEqual([market.pk for market in farmer.markets.all()],
            [market.pk for market in Market.objects.filter(pk=self.market.pk)])


class AgentTestCase(FNCSTestCase):

    def setUp(self):
        super(AgentTestCase, self).setUp()
        self.test_msisdn = '27861234567'
        self.login()

    def test_sales(self):
        response = self.client.get(reverse('fncs:sales'))
        self.assertContains(response, 'Crop sale history')
        self.assertContains(response, 'Agent sale history')

    def test_sales_crops(self):
        response = self.client.get(reverse('fncs:sales_crops'))
        self.assertContains(response, 'No sales')
        # make a sale
        receipt = self.take_in(10, 'boxes', 'tomato')
        sale = utils.sell(receipt, 10, 10)
        response = self.client.get(reverse('fncs:sales_crops'))
        self.assertContains(response, str(receipt.crop))

    def test_sales_agents(self):
        # This view doesn't do much yet
        response = self.client.get(reverse('fncs:sales_agents'))
        self.assertEqual(response.status_code, 200)

    def test_sales_agent_breakdown(self):
        # This view doesn't do much yet
        response = self.client.get(reverse('fncs:sales_agent_breakdown'))
        self.assertEqual(response.status_code, 200)

class PricesTestCase(FNCSTestCase):

    def setUp(self):
        super(PricesTestCase, self).setUp()
        self.test_msisdn = '27861234567'
        self.login()

    def test_market_prices(self):
        response = self.client.get(reverse('fncs:market_prices'))
        self.assertEqual(response.status_code, 200)
        # not available for agents
        self.assertNotContains(response, 'Provide opening price')
        # test availability for market monitors
        actor = self.agent.actor
        market_monitor = MarketMonitor.objects.create(actor=actor)
        response = self.client.get(reverse('fncs:market_prices'))
        self.assertEqual(actor.as_marketmonitor(), market_monitor)
        self.assertContains(response, 'Provide opening price')

    def test_market_sales(self):
        response = self.client.get(reverse('fncs:market_sales'))
        self.assertContains(response, 'No transactions')
        receipt = self.take_in(10,'boxes','oranges')
        transactions = utils.sell(receipt, 10, 10)
        response = self.client.get(reverse('fncs:market_sales'))
        self.assertContains(response, self.market.name)

    def test_market_sale(self):
        response = self.client.get(reverse('fncs:market_sale', kwargs={
            'market_pk': self.market.pk
        }))
        self.assertContains(response, 'No sales recorded yet')
        receipt = self.take_in(10, 'boxes', 'tomato')
        response = self.client.get(reverse('fncs:market_sale', kwargs={
            'market_pk': self.market.pk
        }))
        crops = self.market.crops()
        for crop in crops:
            self.assertContains(response, crop.name)

    def test_crop(self):
        receipt = self.take_in(10, 'boxes', 'apples')
        transaction = utils.sell(receipt, 10, 10)
        response = self.client.get(reverse('fncs:crop', kwargs={
            'market_pk': self.market.pk,
            'crop_pk': receipt.crop.pk,
        }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Average price 10.00 ZMK')
        self.assertContains(response, 'apples sold in boxes')

    @skip("not implemented yet")
    def test_crop_unit(self):
        pass

    @skip("not implemented yet")
    def test_market_offers(self):
        pass

    @skip("not implemented yet")
    def test_market_offer(self):
        pass

    @skip("not implemented yet")
    def test_offer(self):
        pass

    @skip("not implemented yet")
    def test_offer_unit(self):
        pass

    @skip("not implemented yet")
    def test_market_new_offer(self):
        pass

    @skip("not implemented yet")
    def test_market_register_offer(self):
        pass


class FarmerBusinessAdvisorTestCase(FNCSTestCase):
    def setUp(self):
        self.msisdn = '1234567890'
        self.pin = '1234'
        self.fba = utils.create_fba(msisdn=self.msisdn)
        identity = self.fba.actor.get_identity(self.msisdn)
        identity.set_pin(self.pin)
        identity.save()
        self.login()

    def test_available_permissions(self):
        response = self.client.get(reverse('fncs:home'))
        self.assertNotContains(response, 'sales')
        self.assertNotContains(response, 'inventory')
        self.assertContains(response, 'farmers')
        self.assertContains(response, 'market-prices')

class IdentityAuthenticationBackendTestCase(TestCase):

    def test_login_with_identity(self):
        farmer = utils.create_farmer(msisdn='1234')
        farmer.actor.add_identity('6789', '6789')
        # Log in with the new identity
        client = Client()
        client.login(username='6789', password='6789')
        response = client.get(reverse('fncs:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'],
            farmer.actor.user)
