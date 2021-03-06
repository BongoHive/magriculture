from datetime import datetime
import re

from django.test import TestCase
from django.test.client import Client
from django.utils.unittest import skip
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.models import check_password
from magriculture.fncs.models.props import Message

from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import Agent, Farmer, MarketMonitor
from magriculture.fncs.models.geo import Market
from magriculture.fncs.models.props import Message


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
        self.ward = utils.create_ward('test ward', self.district)
        self.market = utils.create_market('test market', self.district)

        self.agent = utils.create_agent(msisdn="+260961234568")
        self.msisdn = self.agent.actor.user.username

        identity = self.agent.actor.get_identity(self.msisdn)
        identity.set_pin(self.pin)
        identity.save()

        self.login_url = '%s?next=%s' % (reverse('login'), reverse('fncs:home'))
        self.farmers = list(create_random_farmers(10, self.agent, self.market))
        self.farmer = self.farmers[0]

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

    def test_login_non_normalised(self):
        self.msisdn = "0961234568"
        self.login()
        response = self.client.get(reverse('fncs:home'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_spaces(self):
        self.msisdn = " 096 123 456 8 "
        self.login()
        response = self.client.get(reverse('fncs:home'))
        self.assertEqual(response.status_code, 200)

    def test_login_without_plus(self):
        self.msisdn = "260961 234568"
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

    def test_user_agent_menu_view(self):
        """
        This tests if a user with agent status is an agent
        according to the request context
        """
        self.login()
        response = self.client.get(reverse('fncs:home'))
        self.assertTrue(response.context["user"].actor.is_agent())

    def test_user_non_agent_menu_view(self):
        """
        This tests if a user without agent status is not an agent
        according to the request context
        """
        User.objects.create_user("non_agent", "non_agent@mail.com", "pass123")
        self.client.login(username="non_agent", password="pass123")
        response = self.client.get(reverse('fncs:home'))
        self.assertFalse(response.context["user"].actor.is_agent())

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
        self.test_msisdn = '09861234567'
        self.normalised_test_msisdn = '+2609861234567'
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

    def test_farmer_creation1(self):
        self.assertFalse(utils.is_farmer(self.test_msisdn))
        response = self.client.get(reverse('fncs:farmer_new'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': self.test_msisdn,
            'msisdn2': '+260891231234',
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': "M",
        })
        farmer = Farmer.objects.get(
            actor__user__username=self.normalised_test_msisdn)
        self.assertEqual(farmer.actor.user.first_name, 'name')
        self.assertEqual(farmer.actor.user.last_name, 'surname')
        self.assertEqual(farmer.gender, 'M')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(utils.is_farmer(self.normalised_test_msisdn))
        self.assertFalse(utils.is_farmer(self.test_msisdn))

    def test_farmer_creation2(self):
        # same test as above but with normalised msisdn
        self.assertFalse(utils.is_farmer(self.normalised_test_msisdn))
        response = self.client.get(reverse('fncs:farmer_new'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': self.normalised_test_msisdn,
            'msisdn2': '+260891231234',
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': "M",
        })
        farmer = Farmer.objects.get(
            actor__user__username=self.normalised_test_msisdn)
        self.assertEqual(farmer.actor.user.first_name, 'name')
        self.assertEqual(farmer.actor.user.last_name, 'surname')
        self.assertEqual(farmer.gender, 'M')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(utils.is_farmer(self.normalised_test_msisdn))
        self.assertFalse(utils.is_farmer(self.test_msisdn))

    def test_farmer_creation3(self):
        # same test as above but with spaces in the number
        self.assertFalse(utils.is_farmer(self.normalised_test_msisdn))
        response = self.client.get(reverse('fncs:farmer_new'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': self.normalised_test_msisdn,
            'msisdn2': '+260 89 123 1234',
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': "M",
        })
        farmer = Farmer.objects.get(
            actor__user__username=self.normalised_test_msisdn)
        self.assertEqual(farmer.actor.user.first_name, 'name')
        self.assertEqual(farmer.actor.user.last_name, 'surname')
        self.assertEqual(farmer.gender, 'M')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(utils.is_farmer(self.normalised_test_msisdn))
        self.assertFalse(utils.is_farmer(self.test_msisdn))

    def test_farmer_creation4(self):
        # same test as above but with a '+' missing for number
        self.assertFalse(utils.is_farmer(self.normalised_test_msisdn))
        response = self.client.get(reverse('fncs:farmer_new'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': self.normalised_test_msisdn,
            'msisdn2': '260 89 123 1234',
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': "M",
        })
        farmer = Farmer.objects.get(
            actor__user__username=self.normalised_test_msisdn)
        self.assertEqual(farmer.actor.user.first_name, 'name')
        self.assertEqual(farmer.actor.user.last_name, 'surname')
        self.assertEqual(farmer.gender, 'M')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(utils.is_farmer(self.normalised_test_msisdn))
        self.assertFalse(utils.is_farmer(self.test_msisdn))

    def test_farmer_location_search_no_query(self):
        response = self.client.get(self.farmer_url('location_search'))
        self.assertContains(response, 'Search for ward or district:')
        self.assertNotContains(response, 'Select ward or district')

    def test_farmer_location_search_with_query(self):
        response = self.client.post(self.farmer_url('location_search'), {
            'search': self.ward.name.lower()})
        self.assertContains(response, 'Search for ward or district:')
        self.assertContains(response, 'Select ward or district:')
        self.assertContains(response, '%s (ward)' % (self.ward.name,))

    def test_farmer_location_search_with_query_but_no_result(self):
        response = self.client.post(self.farmer_url('location_search'), {
            'search': 'unknown'})
        self.assertContains(response, 'Search for ward or district:')
        self.assertContains(response, 'No locations found. '
                            'Please search again.')

    def test_farmer_location_save_ward(self):
        response = self.client.post(self.farmer_url('location_save'), {
            'search': self.ward.name.lower(),
            'location': 'ward:%d' % self.ward.pk}, follow=True)
        wards = self.farmer.wards.all()
        self.assertEqual(wards.count(), 2)
        self.assertTrue(wards.get(name=self.ward.name))
        self.assertRedirects(response, self.farmer_url('sales'))

    def test_farmer_location_save_district(self):
        response = self.client.post(self.farmer_url('location_save'), {
            'search': self.district.name.lower(),
            'location': 'district:%d' % self.district.pk}, follow=True)

        districts = self.farmer.districts.all()
        self.assertEqual(districts.count(), 2)
        self.assertTrue(districts.get(name=self.district.name))
        self.assertRedirects(response, self.farmer_url('sales'))


    def test_farmer_location_delete_confirm_district(self):
        response = self.client.get(self.farmer_url('location_delete_confirm',
                                                    district_pk=self.district.pk),
                                   follow=True)

        districts = self.farmer.districts.all()
        self.assertEqual(districts.count(), 1)
        self.assertEquals('/farmers/%s/location/%s/delete/confirm' % (self.farmer.pk,
                                                                      self.district.pk),
                          response.request["PATH_INFO"])
        self.assertEquals(response.context["location_delete_form"].data["district_pk"],
                          unicode(self.district.pk))

    def test_farmer_location_delete_district(self):
        # Making sure that a farmer has a district
        districts = self.farmer.districts.all()
        self.assertEqual(districts.count(), 1)

        # District name that will be used
        district_name = districts[0].name

        response = self.client.post(self.farmer_url('location_delete'), {
            'district_pk': districts[0].pk}, follow=True)

        districts = self.farmer.districts.all()
        self.assertEqual(districts.count(), 0)
        self.assertContains(response, "%s district has been deleted from %s" %
                          (district_name, self.farmer.actor.name))


    def test_farmer_location_delete_district_no_post_data(self):
        # Testing to see if district is not actually deleted
        districts = self.farmer.districts.all()
        self.assertEqual(districts.count(), 1)

        response = self.client.post(self.farmer_url('location_delete'), follow=True)

        districts = self.farmer.districts.all()
        self.assertEqual(districts.count(), 1)
        self.assertContains(response, "Please select a district for deletion.")

    def test_farmer_location_delete_district_on_get(self):
        # Testing to see that district is not actally deleted

        districts = self.farmer.districts.all()
        self.assertEqual(districts.count(), 1)

        response = self.client.get(self.farmer_url('location_delete'), follow=True)

        districts = self.farmer.districts.all()
        self.assertEqual(districts.count(), 1)
        self.assertContains(response, "Please select a district for deletion.")

    def test_farmer_id_number(self):
        response = self.client.post(self.farmer_url('edit'), {
            'msisdn1': self.test_msisdn,
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'id_number': '123456789',
            'gender': 'M',
            })
        self.assertRedirects(response, self.farmer_url('crops'))
        farmer = Farmer.objects.get(pk=self.farmer.pk)
        self.assertEqual(farmer.id_number, '123456789')
        self.assertEqual(farmer.gender, 'M')

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

    def test_farmer_sales(self):
        response = self.client.get(self.farmer_url('sales'))
        self.assertContains(response, 'Crop Intake')
        self.assertContains(response, reverse('fncs:inventory_intake'))

    def test_farmer_sale(self):
        receipt = self.take_in(10, 'boxes', 'tomato')
        sale = utils.sell(receipt, 10, 10)
        response = self.client.get(self.farmer_url('sale', sale_pk=sale.pk))
        self.assertContains(response, '10 boxes of tomato', status_code=200)

    def test_farmer_new_message(self):
        # Check that messages table is empty
        self.assertEqual(Message.objects.all().count(), 0)
        response = self.client.post(self.farmer_url('new_message',
                                                    farmer_pk=self.farmer.pk),
                                    {"content": "This is the content"},
                                    follow=True)
        messages = Message.objects.all()
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages[0].content, "This is the content")
        self.assertRedirects(response, self.farmer_url('sales', farmer_pk=self.farmer.pk))

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
        # Making sure the messages Model is empty
        self.assertEquals(Message.objects.all().count(), 0)
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

        # As all the tomatoes have been sold, expecting two messages
        messages = Message.objects.all()
        self.assertEquals(messages.count(), 2)
        content = ["10 boxes(s) of tomato all sold by name surname",
                    "name surname sold 10 boxes(s) of tomato for 100.00 (10.00 per boxes)"]
        self.assertEquals(sorted(content),
                          sorted([obj.content for obj in messages]))

    def test_farmer_new_sale_detail_with_remaining_stock(self):
        self.assertEquals(Message.objects.all().count(), 0)
        receipt = self.take_in(10, 'boxes', 'tomato')
        self.assertFalse(receipt.reconciled)
        sale_url = '%s?crop_receipt=%s' % (self.farmer_url('new_sale_detail'),
            receipt.pk)

        post_args = format_timestamp('created_at', datetime.now())
        amount = receipt.amount - 5
        post_args.update({
            'crop_receipt': receipt.pk,
            'price': 10.0,
            'amount': amount,
            'market': self.market.pk,
        })

        response = self.client.post(sale_url, post_args, follow=True)

        self.assertRedirects(response, self.farmer_url('sales'))
        transaction = receipt.farmer.transactions().latest()
        self.assertEqual(transaction.crop_receipt.pk, receipt.pk)
        self.assertEqual(transaction.price, 10)
        self.assertEqual(transaction.amount, amount)
        self.assertEqual(transaction.total, 10 * amount)
        self.assertFalse(transaction.crop_receipt.reconciled)

        # As all the tomatoes have not been sold, only expecting one message
        messages = Message.objects.all()
        self.assertEquals(messages.count(), 1)
        self.assertEquals(messages[0].content,
                          "name surname sold 5 boxes(s) of tomato for 50.00 (10.00 per boxes)")

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
            'msisdn1': '1',
            'markets': [self.market.pk],
            'gender': 'M',
        })
        self.assertRedirects(response, self.farmer_url('crops'))
        farmer = Farmer.objects.get(pk=self.farmer.pk)
        user = farmer.actor.user
        self.assertEqual(user.first_name, 'n')
        self.assertEqual(user.last_name, 'sn')
        self.assertEqual(user.username, '1')
        self.assertEqual(farmer.gender, 'M')
        self.assertEqual([market.pk for market in farmer.markets.all()],
            [market.pk for market in Market.objects.filter(pk=self.market.pk)])

    def test_farmer_matching_on_msisdn1(self):
        farmer = utils.create_farmer(msisdn='+260961234567')
        msisdn = farmer.actor.get_msisdns()[0]
        self.assertTrue(utils.is_farmer(msisdn))
        self.assertFalse(utils.is_farmer('0961234567'))
        # Now we try & recreate a farmer with a known MSISDN, should give us a
        # matching suggestion
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': msisdn,
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': 'M',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, farmer.actor.name)

    def test_farmer_matching_on_msisdn2(self):
        # This test is identical to the one above, except we are checking with
        # a non-normalised msisdn to ensure matching works then, too.
        farmer = utils.create_farmer(msisdn='+260961234567')
        msisdn = farmer.actor.get_msisdns()[0]
        self.assertTrue(utils.is_farmer(msisdn))
        self.assertFalse(utils.is_farmer('0961234567'))
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': '0961234567',
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': 'M',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, farmer.actor.name)

    def test_farmer_matching_on_msisdn3(self):
        # This test is identical to the one above, except we are checking with
        # a msisdn with spaces to ensure matching works then, too.
        farmer = utils.create_farmer(msisdn='+260961234567')
        msisdn = farmer.actor.get_msisdns()[0]
        self.assertTrue(utils.is_farmer(msisdn))
        self.assertFalse(utils.is_farmer('096 123 4567'))
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': '096 123 4567',
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': 'M',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, farmer.actor.name)

    def test_farmer_matching_on_msisdn4(self):
        # This test is identical to the one above, except we are checking with
        # a msisdn starting on 260 to ensure matching works then, too.
        farmer = utils.create_farmer(msisdn='+260961234567')
        msisdn = farmer.actor.get_msisdns()[0]
        self.assertTrue(utils.is_farmer(msisdn))
        self.assertFalse(utils.is_farmer('260 96 123 4567'))
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': '260 96 123 4567',
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': 'M',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, farmer.actor.name)

    def test_farmer_matching_on_id_number(self):
        farmer = utils.create_farmer()
        farmer.id_number = '1234'
        farmer.save()
        # Now we try & recreate a farmer with a known MSISDN, should give us a
        # matching suggestion
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': '123123123123',
            'id_number': farmer.id_number, # same as previous farmer
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'gender': 'M',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, farmer.actor.name)

    def test_farmer_matching_redirect(self):
        farmer = utils.create_farmer()
        msisdn = farmer.actor.get_msisdns()[0]
        other_agent = utils.create_agent(msisdn='1')
        farmer.operates_at(self.market, other_agent)
        response = self.client.post(reverse('fncs:farmer_new'), {
            'msisdn1': msisdn,
            'name': 'name',
            'surname': 'surname',
            'markets': [self.market.pk],
            'matched_farmer': farmer.pk,
            'gender': 'M',
            })
        self.assertRedirects(response, reverse('fncs:farmer_edit', kwargs={
            'farmer_pk': farmer.pk,
            }))
        farmer = Farmer.objects.get(pk=farmer.pk)
        self.assertEqual(set([other_agent, self.agent]),
                         set(farmer.agent_farmer.all()))


class AgentTestCase(FNCSTestCase):

    def setUp(self):
        super(AgentTestCase, self).setUp()
        self.test_msisdn = '27861234567'
        self.login()

        self.user = utils.create_generic_user()
        self.user.is_superuser = True
        self.user.save()

    def test_agent_creation(self):
        # Agents can only be created by extension officers or super users
        login = self.client.login(username=self.user.username, password=utils.PASSWORD)
        self.assertTrue(login)

        self.assertFalse(utils.is_agent(self.test_msisdn))
        response = self.client.get(reverse('fncs:agent_new'))
        self.assertEqual(response.status_code, 200)
        for farmer in Farmer.objects.all():
            self.assertContains(response, unicode(farmer))
        for market in Market.objects.all():
            self.assertContains(response, unicode(market))
        response = self.client.post(reverse('fncs:agent_new'), {
            'msisdn': self.test_msisdn,
            'name': 'name',
            'surname': 'surname',
            'farmers': [self.farmer.pk],
            'markets': [self.market.pk],
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(utils.is_agent(self.test_msisdn))

    def test_agent_edit(self):
        # Agents can only be edited by extension officers or super users
        login = self.client.login(username=self.user.username, password=utils.PASSWORD)
        self.assertTrue(login)

        agent_url = reverse('fncs:agent', kwargs={'agent_pk': self.agent.pk})
        response = self.client.get(agent_url)
        user = self.agent.actor.user
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.username)
        response = self.client.post(agent_url, {
            'name': 'n',
            'surname': 'sn',
            'msisdn': '1',
            'farmers': [self.farmer.pk],
            'markets': [self.market.pk],
        })
        self.assertRedirects(response, reverse("fncs:agents"))
        agent = Agent.objects.get(pk=self.agent.pk)
        user = agent.actor.user
        self.assertEqual(user.first_name, 'n')
        self.assertEqual(user.last_name, 'sn')
        self.assertEqual(user.username, '1')
        self.assertEqual([farmer.pk for farmer in agent.farmers.all()],
                         [self.farmer.pk])
        self.assertEqual([market.pk for market in agent.markets.all()],
                         [self.market.pk])

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
        receipt = self.take_in(10, 'boxes', 'oranges')
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
        self.msisdn = '+260234567890'
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
        farmer = utils.create_farmer(msisdn='+260121231234')
        farmer.actor.add_identity('+260676786789', '6789')
        # Log in with the new identity
        client = Client()
        client.login(username='+260676786789', password='6789')
        response = client.get(reverse('fncs:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'],
                         farmer.actor.user)


class TestExtensionOfficerLogin(TestCase):
    def setUp(self):
        pass

    def test_login_non_extension_officer(self):
        user = utils.create_generic_user()
        login = self.client.login(username=user.username,
                                  password=utils.PASSWORD)
        self.assertTrue(login)
        response = self.client.get(reverse('fncs:home'))
        self.assertFalse(response.context["user"].actor.is_extensionofficer())

    def test_login_extension_officer(self):
        officer = utils.create_extension_officer()
        login = self.client.login(username=officer.actor.user.username,
                                  password=utils.PASSWORD)
        self.assertTrue(login)

        response = self.client.get(reverse('fncs:home'))
        self.assertTrue(response.context["user"].actor.is_extensionofficer())

    def test_non_extension_officer_get_new_markets(self):
        user = utils.create_generic_user()
        login = self.client.login(username=user.username,
                                  password=utils.PASSWORD)
        self.assertTrue(login)
        response = self.client.get(reverse('fncs:market_new'), follow=True)
        self.assertRedirects(response, reverse("fncs:home"))
        self.assertEquals(response.context["messages"]._loaded_data[0].message,
                          "Sorry you don't have rights to view this part of the system.")

    def test_extension_officer_get_new_markets(self):
        officer = utils.create_extension_officer()
        login = self.client.login(username=officer.actor.user.username,
                                  password=utils.PASSWORD)
        self.assertTrue(login)
        response = self.client.get(reverse('fncs:market_new'), follow=True)
        self.assertEqual(response.request.get("PATH_INFO"), reverse('fncs:market_new'))


class TestExtensionOfficerMarkets(TestCase):
    def setUp(self):
        self.province = utils.create_province('test province')
        self.district = utils.create_district('test district', self.province)
        self.ward = utils.create_ward('test ward', self.district)
        self.market = utils.create_market('test market', self.district)

        self.officer = utils.create_extension_officer()
        self.client.login(username=self.officer.actor.user.username, password=utils.PASSWORD)

    def test_add_new_markets(self):
        data = {"name": "New Market",
                "district": self.district.id}
        response = self.client.post(reverse('fncs:market_new'), data=data, follow=True)
        market = Market.objects.get(name="New Market")

        self.assertEquals(market.district, self.district)
        self.assertRedirects(response, reverse("fncs:home"))
        self.assertEquals(response.context["messages"]._loaded_data[0].message,
                          "A new market has been created.")


class TestExtensionOfficersAgents(TestCase):
    def setUp(self):
        self.province = utils.create_province('test province')
        self.district = utils.create_district('test district', self.province)
        self.ward = utils.create_ward('test ward', self.district)
        self.market = utils.create_market('test market', self.district)

        self.agent = utils.create_agent()

        self.farmers = list(create_random_farmers(10, self.agent, self.market))
        self.farmer = self.farmers[0]

        self.officer = utils.create_extension_officer()
        self.client.login(username=self.officer.actor.user.username, password=utils.PASSWORD)


    def test_add_new_agent(self):
        data = {"name": "name_first",
                "surname": "name_surname",
                "msisdn": "1234567890",
                "farmers": [self.farmer.pk],
                "markets": [self.market.pk]}
        response = self.client.post(reverse('fncs:agent_new'), data=data, follow=True)
        self.assertEquals(response.context["messages"]._loaded_data[0].message,
                          "Agent Created")
        self.assertRedirects(response, reverse("fncs:agents"))
        new_agent = User.objects.get(username=data["msisdn"])
        self.assertEquals(new_agent.first_name, "name_first")
        self.assertEquals(new_agent.last_name, "name_surname")
        self.assertTrue(new_agent.actor.is_agent())
        self.assertFalse(new_agent.actor.is_extensionofficer())
        self.client.logout()

        # Assumes that if message is stored message has been sent
        # There is a current flaw in teh code where the sender and
        # recipient is the same actor
        messages = Message.objects.get(recipient=new_agent.actor)
        self.assertEquals(messages.sender, new_agent.actor)
        self.assertIn('You have been registered and your pin is - ',
                      messages.content)

        reg_pin = re.compile(r"\d\d\d\d")
        pin = reg_pin.search(messages.content).group()
        login_agent = self.client.login(username=data["msisdn"], password=pin)
        self.assertTrue(login_agent)
