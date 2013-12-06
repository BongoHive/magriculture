# Python
from datetime import datetime, timedelta

# Django
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# Project
from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import (Actor, Farmer, FarmerGroup,
                                             Identity)
from magriculture.fncs.models.props import Message, GroupMessage, Note, Crop
from magriculture.fncs.errors import ActorException
from magriculture.fncs import errors
from nose.tools import raises
from magriculture.fncs.models.geo import District

class ActorTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_actor_creation(self):
        user = User.objects.create_user('username', 'email@domain.com')
        actor = user.get_profile()
        self.assertTrue(isinstance(actor, Actor))


class TestSendMessage(TestCase):
    """
    Test Send Message to Farmer Groups
    """
    fixtures = ["test_province.json",
                "test_district.json",
                "test_ward.json",
                "test_zone.json",
                "test_rpiarea.json",
                "test_auth_user.json",
                "test_actor.json",
                "test_agent",
                "test_farmer.json",
                "test_crop_unit.json",
                "test_crop.json",
                "test_market.json",
                "test_crop_receipt.json",
                "test_transaction.json"]

    def setUp(self):
        self.client.login(username="m", password="m")
        self.user = User.objects.get(username="m")
        self.actor = self.user.get_profile()
        self.agent = self.actor.as_agent()
        self.crop = Crop.objects.get(name="Coffee")
        self.district = District.objects.get(name="Kafue")
        self.district_2 = District.objects.get(name="Nchelenge")

    def test_send_farmer_group_message_get_initial_form(self):
        url = reverse("fncs:group_message_new")
        response = self.client.get(url, follow=True)
        response_crops = [(crop.id, crop.name) for crop in
                          response.context["form"].fields["crop"].queryset]
        db_crops = [(crop.id, crop.name) for crop in
                    Crop.objects.filter(farmer_crop__agent_farmer=self.agent)]
        self.assertEquals(sorted(response_crops), sorted(db_crops))

    def test_send_farmer_group_message_new_empty(self):
        url = reverse("fncs:group_message_new")
        response = self.client.post(url, follow=True)
        response_crops = [(crop.id, crop.name) for crop in
                          response.context["form"].fields["crop"].queryset]
        db_crops = [(crop.id, crop.name) for crop in
                    Crop.objects.filter(farmer_crop__agent_farmer=self.agent)]
        self.assertEquals(sorted(response_crops), sorted(db_crops))
        self.assertEquals(response.context["form"].errors["crop"],
                          [u'This field is required.'])

    def test_send_farmer_group_message_new(self):
        """
        Testing the New group message based on filters
        """
        data = {"crop": self.crop.pk}

        url = reverse("fncs:group_message_new")
        response = self.client.post(url, data=data, follow=True)

        form_data = response.context["form"].cleaned_data
        self.assertEquals(form_data["crop"], self.crop)
        self.assertEquals(form_data["district"], [])
        self.assertEquals(response.context["choose_district"],
                          True)
        self.assertEqual(response.request["PATH_INFO"], url)

        dt_queryset = response.context["form"].fields["district"].queryset
        response_district = [(d.id, d.name) for d in dt_queryset]
        db_district = [(d.id, d.name) for d in
                       (District.
                        objects.
                        filter(farmer_district__agent_farmer=self.agent).
                        filter(farmer_district__crops=self.crop).
                        all().
                        distinct())]

        self.assertEquals(sorted(response_district), sorted(db_district))

        data_2 = {"district": [self.district.pk, self.district_2.pk],
                  "crop": self.crop.pk}
        response_2 = self.client.post(url, data=data_2)

        url_write = reverse("fncs:group_message_write")
        self.assertRedirects(response_2,
                             "%s?crop=1&district=5&district=4" % url_write)

        response_3 = self.client.post(url, data=data_2, follow=True)
        self.assertIn("content", response_3.context["form"].fields)
        self.assertEquals(response_3.request["QUERY_STRING"],
                          "district=5&district=4&crop=1")

    def test_send_farmer_group_message_write(self):
        """
        Testing the write new message
        """
        url_write = reverse("fncs:group_message_write")
        data = {"content": "Test Send Message"}
        response = self.client.post("%s?district=5&district=4&crop=1" % url_write,
                                    data=data,
                                    follow=True)

        farmergrp = FarmerGroup.objects.all()
        self.assertEquals(farmergrp.count(), 1)
        self.assertEquals(farmergrp[0].crop, self.crop)
        grp_district = [(d.id, d.name) for d in farmergrp[0].district.all()]
        self.assertEquals(sorted(grp_district),
                          sorted([(self.district.pk, self.district.name),
                                 (self.district_2.pk, self.district_2.name)]))

        self.assertEquals(farmergrp[0].agent,
                          response.context["user"].actor.as_agent())
        self.assertEquals(farmergrp[0].name, u'Coffee farmers in Nchelenge & Kafue ')
        self.assertTrue(GroupMessage.objects.count(), 2)
        self.assertTrue(self.agent.actor.sentmessages_set.count(), 2)

        # Testing if the filtered farmers is equal to the posted farmers
        farmers = (Farmer.objects.
                   filter(agent_farmer=self.agent,
                          crops=self.crop,
                          districts__in=[self.district.pk, self.district_2.pk]).
                   all().
                   distinct())

        # Data structure below is [(username, content, number_of_messages_sent)]
        message_list = [(obj.recipient.user.username,
                         obj.content, 1) for obj in Message.objects.all()]
        farmers_list = [(obj.actor.user.username,
                         data["content"],
                         obj.actor.receivedmessages_set.count())
                        for obj in farmers]

        self.assertEquals(sorted(message_list), sorted(farmers_list))


class TestCreateFarmerWithFixtureData(TestCase):
    """
    Test Send Message to Farmer Groups
    """
    fixtures = ["test_province.json",
                "test_district.json",
                "test_ward.json",
                "test_zone.json",
                "test_rpiarea.json",
                "test_auth_user.json",
                "test_actor.json",
                "test_agent",
                "test_farmer.json",
                "test_crop_unit.json",
                "test_crop.json",
                "test_market.json",
                "test_crop_receipt.json",
                "test_transaction.json"]

    def setUp(self):
        self.client.login(username="m", password="m")
        self.user = User.objects.get(username="m")
        self.actor = self.user.get_profile()
        self.agent = self.actor.as_agent()
        self.crop = Crop.objects.get(name="Coffee")
        self.district = District.objects.get(name="Kafue")
        self.district_2 = District.objects.get(name="Nchelenge")

    def test_farmer_creation_duplicate_null_id_number(self):
        """
        Replicate duplicate ID number bug, only occurs in
        post data as None is converted to a string.
        """
        utils.create_farmer(name="joe_1")

        url = reverse("fncs:farmer_new")
        data_1 = {"name": "name_1",
                  "surname": "surname_1",
                  "msisdn1": "123456781",
                  "gender": "M",
                  "markets": [1, 2]}
        self.client.post(url, data=data_1, follow=True)
        farmer = Farmer.objects.get(actor__user__username="123456781")
        self.assertEquals(farmer.actor.user.first_name, "name_1")


class AgentTestCase(TestCase):
    def test_agent_creation(self):
        agent = utils.create_agent()
        self.assertEquals(agent.farmers.count(), 0)
        self.assertEquals(agent.markets.count(), 0)

    def test_agent_sale(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.districts.all()[0])
        agent = utils.create_agent()

        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        price = 20
        amount = 10

        # create inventory
        receipt = agent.take_in_crop(market, farmer, amount, unit, crop)
        self.assertTrue(receipt.remaining_inventory(), 10)
        transaction = agent.register_sale(receipt, amount, price)

        self.assertTrue(agent.is_selling_for(farmer, market))
        self.assertIn(market, agent.markets.all())
        self.assertIn(farmer, agent.farmers.all())
        # test the transaction aspect
        self.assertEquals(transaction.total, 200.0)
        self.assertEquals(transaction.price, price)
        self.assertEquals(transaction.amount, amount)
        # test the selling out of the inventory
        crop_receipt = transaction.crop_receipt
        self.assertEquals(crop_receipt.crop, crop)
        self.assertEquals(crop_receipt.unit, unit)
        self.assertEquals(crop_receipt.agent, agent)
        self.assertEquals(crop_receipt.farmer, farmer)
        self.assertEquals(crop_receipt.market, market)

        # had 20 crops in inventory, inventory should be reconciled
        # and the calculated stock count should reflect this
        self.assertEquals(crop_receipt.amount, 10)
        self.assertTrue(crop_receipt.reconciled)
        self.assertEquals(crop_receipt.remaining_inventory(), 0)

        self.assertAlmostEqual(transaction.created_at, datetime.now(),
                               delta=timedelta(seconds=2))
        self.assertIn(transaction, farmer.transactions())
        self.assertTrue(farmer.is_growing_crop(crop))
        self.assertIn(transaction, agent.sales_for(farmer))

    def test_actor_as_agent(self):
        agent = utils.create_agent()
        actor = agent.actor
        self.assertEquals(agent, actor.as_agent())

    @raises(errors.ActorException)
    def test_actor_without_agent(self):
        """
        This should raise an ActorException for agent doesn't exist
        """
        user = User.objects.create_user("27721111111",
                                        "27721111111@mail.com",
                                        "pass123")
        login = self.client.login(username=user.username,
                                  password="pass123")
        self.assertTrue(login)
        url_messages = reverse("fncs:farmers")
        self.client.get(url_messages)

    def test_agent_crop_receipt_inventory(self):
        farmer1 = utils.create_farmer(msisdn="27700000000")
        farmer2 = utils.create_farmer(msisdn="27700000001")
        market = utils.create_market("market", farmer1.districts.all()[0])
        agent = utils.create_agent()
        receipt1 = utils.take_in(market, agent, farmer1, 10, 'box', 'tomato')
        receipt2 = utils.take_in(market, agent, farmer2, 10, 'box', 'onion')
        self.assertEqual([receipt1],
                         list(agent.cropreceipts_available_for(farmer1)))
        self.assertEqual([receipt2],
                         list(agent.cropreceipts_available_for(farmer2)))

    def test_send_farmer_message(self):
        farmer = utils.create_farmer()
        agent = utils.create_agent()
        message = agent.send_message_to_farmer(farmer, 'hello world')
        self.assertIn(message, Message.objects.filter(sender=agent.actor,
                                                      recipient=farmer.actor))
    """
    UPDATE WHEN CHANGE FARMER GROUP
    """
    # def test_send_farmergroup_message(self):
    #     farmer1 = utils.create_farmer(msisdn='1')
    #     farmer2 = utils.create_farmer(msisdn='2')
    #     farmergroups = FarmerGroup.objects.all()
    #     agent = utils.create_agent()
    #     agent.send_message_to_farmergroups(farmergroups, 'hello world')
    #     self.assertTrue(agent.actor.sentmessages_set.count(), 2)
    #     self.assertTrue(GroupMessage.objects.count(), 2)
    #     self.assertTrue(farmer1.actor.receivedmessages_set.count(), 1)
    #     self.assertTrue(farmer2.actor.receivedmessages_set.count(), 1)

    def test_write_note(self):
        farmer = utils.create_farmer()
        agent = utils.create_agent()
        note = agent.write_note(farmer, 'this is a note about the farmer')
        self.assertIn(note, Note.objects.all())
        self.assertIn(note, farmer.actor.attachednote_set.all())
        self.assertIn(note, agent.notes_for(farmer))


class MarketMonitorTestCase(TestCase):

    def test_market_monitor_registration(self):
        monitor = utils.create_market_monitor()
        province = utils.create_province("province")
        rpiarea = utils.create_rpiarea("rpiarea")
        rpiarea.provinces.add(province)
        district = utils.create_district("district", province)
        market = utils.create_market("market", district)

        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        price_floor = 150
        price_ceiling = 200

        offer = monitor.register_offer(market, crop, unit, price_floor,
                                       price_ceiling)
        self.assertTrue(monitor.is_monitoring(market))
        self.assertIn(market, monitor.markets.all())
        for rpiarea in market.rpiareas():
            self.assertIn(rpiarea, monitor.rpiareas.all())
        self.assertEquals(offer.price_floor, 150.0)
        self.assertEquals(offer.price_ceiling, 200.0)
        self.assertEquals(offer.crop, crop)
        self.assertEquals(offer.unit, unit)
        self.assertEquals(offer.market, market)
        self.assertAlmostEqual(offer.created_at, datetime.now(),
                               delta=timedelta(seconds=2))


class FarmerBusinessAdvisorTestCase(TestCase):

    def test_fba_role(self):
        fba = utils.create_fba()
        self.assertEquals(fba.farmers.count(), 0)

    def test_fba_farmer_registration(self):
        fba1 = utils.create_fba(msisdn='0')
        fba2 = utils.create_fba(msisdn='1')
        farmer1 = utils.create_farmer(msisdn='1234', name='farmer1')
        farmer2 = utils.create_farmer(msisdn='5678', name='farmer2')

        # Each should register 1 farmer first
        fba1.register_farmer(farmer1)
        fba2.register_farmer(farmer2)
        # Then the second farmer
        fba1.register_farmer(farmer2)
        fba2.register_farmer(farmer1)

        # both should 'know' each farmer
        farmers = set([farmer1, farmer2])
        self.assertEqual(farmers, set(fba1.get_farmers()))
        self.assertEqual(farmers, set(fba2.get_farmers()))

        # Each should only have 1 farmer as a registered farmer
        self.assertEqual([farmer1], list(fba1.get_registered_farmers()))
        self.assertEqual([farmer2], list(fba2.get_registered_farmers()))


class FarmerTestCase(TestCase):

    def test_farmer_create_helper(self):
        rpiarea = utils.create_rpiarea("rpiarea")
        zone = utils.create_zone("zone", rpiarea)
        province = utils.create_province("province")
        district = utils.create_district("district", province)
        ward = utils.create_ward("ward", district)
        self.assertFalse(Farmer.objects.exists())
        farmer1 = Farmer.create("0761234567", "name", "surname")
        self.assertTrue(Farmer.objects.count(), 1)
        self.assertEqual(farmer1.actor.name, 'name surname')
        farmer2 = Farmer.create("0761234567", "new name", "new surname")
        self.assertTrue(Farmer.objects.count(), 1)
        self.assertEqual(farmer2.actor.name, 'new name new surname')

    def test_farmer_creation(self):
        farmer = utils.create_farmer(name="joe")
        self.assertEquals(farmer.actor.user.first_name, "joe")
        self.assertEquals(farmer.agent_farmer.count(), 0)

    def test_farmer_match(self):
        def match(*args, **kw):
            return sorted(Farmer.match(*args, **kw),
                          key=lambda x: x.actor.user.first_name)

        joe = utils.create_farmer(name="joe", msisdn="1")
        [joe_msisdn] = joe.actor.get_msisdns()
        bob = utils.create_farmer(name="bob", msisdn="2", id_number="1234")
        self.assertEqual(match(), [])
        self.assertEqual(match(id_number=bob.id_number), [bob])
        self.assertEqual(match(msisdns=[joe_msisdn]), [joe])
        self.assertEqual(match(msisdns=[joe_msisdn], id_number=bob.id_number),
                         [bob, joe])

    def test_farmer_agent_link(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.districts.all()[0])
        agent = utils.create_agent()

        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        amount = 10

        agent.take_in_crop(market, farmer, amount, unit, crop)

        self.assertTrue(agent.is_selling_for(farmer, market))
        self.assertIn(market, agent.markets.all())
        self.assertIn(farmer, agent.farmers.all())
        self.assertIn(market, farmer.markets.all())

    def test_farmer_districts(self):
        province = utils.create_province("province")
        district1 = utils.create_district("district 1", province)
        market1 = utils.create_market("market 1", district1)

        district2 = utils.create_district("district 2", province)
        market2 = utils.create_market("market 2", district2)

        farmer = utils.create_farmer()
        agent1 = utils.create_agent("agent 1")
        agent2 = utils.create_agent("agent 2")

        farmer.operates_at(market1, agent1)
        farmer.operates_at(market2, agent2)

        self.assertEquals(farmer.market_districts().count(), 2)
        self.assertIn(district1, farmer.market_districts())
        self.assertIn(district2, farmer.market_districts())

    def test_farmer_grows_crops(self):
        farmer = utils.create_farmer()
        crop = utils.random_crop()
        farmer.grows_crop(crop)
        self.assertIn(crop, farmer.crops.all())

    def test_farmer_market_setting(self):
        farmer = utils.create_farmer()
        market1 = utils.create_market("market 1", farmer.districts.all()[0])
        market2 = utils.create_market("market 2", farmer.districts.all()[0])
        market3 = utils.create_market("market 3", farmer.districts.all()[0])
        # prime the farmer with 1 market
        farmer.markets.add(market1)
        # test the destructive set
        farmer.operates_at_markets_exclusively([market2, market3])
        self.assertNotIn(market1, farmer.markets.all())
        self.assertIn(market2, farmer.markets.all())
        self.assertIn(market3, farmer.markets.all())

    def test_farmer_crop_setting(self):
        farmer = utils.create_farmer()
        crop1 = utils.create_crop("apples")
        crop2 = utils.create_crop("oranges")
        crop3 = utils.create_crop("potatoes")
        farmer.grows_crop(crop1)
        self.assertIn(crop1, farmer.crops.all())
        farmer.grows_crops_exclusively([crop2, crop3])
        self.assertNotIn(crop1, farmer.crops.all())
        self.assertIn(crop2, farmer.crops.all())
        self.assertIn(crop3, farmer.crops.all())


class IdentityTestCase(ActorTestCase):

    def test_identity_pin_auth(self):
        farmer = utils.create_farmer()
        identity = Identity(actor=farmer.actor, msisdn='1234')
        identity.set_pin('5678')
        identity.save()
        self.assertTrue(identity.check_pin('5678'))
        self.assertFalse(identity.check_pin('4567'))

    def test_find_identity(self):
        farmer = utils.create_farmer()
        identity = farmer.actor.add_identity('1234', '1234')

        self.assertEquals(farmer.actor.get_identity('1234'), identity)
        self.assertEquals(Actor.find('1234'), farmer.actor)
        self.assertEquals(Actor.find_with_pin('1234', '1234'), farmer.actor)
        self.assertRaises(ActorException, Actor.find_with_pin, '1234',
                          'bad-pin')
