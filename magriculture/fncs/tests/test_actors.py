from django.test import TestCase
from django.contrib.auth.models import User
from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import Actor, Farmer, FarmerGroup
from magriculture.fncs.models.props import Message, GroupMessage, Note
from datetime import datetime, timedelta

class ActorTestCase(TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_actor_creation(self):
        user = User.objects.create_user('username','email@domain.com')
        actor = user.get_profile()
        self.assertTrue(isinstance(actor, Actor))
    

class AgentTestCase(TestCase):
    def test_agent_creation(self):
        agent = utils.create_agent()
        self.assertEquals(agent.farmers.count(), 0)
        self.assertEquals(agent.markets.count(), 0)
    
    def test_agent_sale(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.farmergroup.district)
        agent = utils.create_agent()

        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        price = 20
        amount = 10

        transaction = agent.register_sale(market, farmer, crop, unit, price, amount)
        self.assertTrue(agent.is_selling_for(farmer, market))
        self.assertIn(market, agent.markets.all())
        self.assertIn(farmer, agent.farmers.all())
        self.assertEquals(transaction.total, 200.0)
        self.assertEquals(transaction.price, price)
        self.assertEquals(transaction.crop, crop)
        self.assertEquals(transaction.unit, unit)
        self.assertEquals(transaction.agent, agent)
        self.assertEquals(transaction.farmer, farmer)
        self.assertEquals(transaction.market, market)
        self.assertEquals(transaction.amount, amount)
        self.assertAlmostEqual(transaction.created_at, datetime.now(),
            delta=timedelta(seconds=2))
        self.assertIn(transaction, farmer.transactions())
        self.assertTrue(farmer.is_growing_crop(crop))
    
    def test_actor_as_agent(self):
        agent = utils.create_agent()
        actor = agent.actor
        self.assertEquals(agent, actor.as_agent())
    
    def test_send_farmer_message(self):
        farmer = utils.create_farmer()
        agent = utils.create_agent()
        message = agent.send_message_to_farmer(farmer, 'hello world')
        self.assertIn(message, Message.objects.filter(sender=agent.actor,
            recipient=farmer.actor))
    
    def test_send_farmergroup_message(self):
        farmer1 = utils.create_farmer(farmergroup_name="group 1")
        farmer2 = utils.create_farmer(farmergroup_name="group 2")
        farmergroups = FarmerGroup.objects.all()
        agent = utils.create_agent()
        agent.send_message_to_farmergroups(farmergroups, 'hello world')
        self.assertTrue(agent.actor.sentmessages_set.count(), 2)
        self.assertTrue(GroupMessage.objects.count(), 2)
        self.assertTrue(farmer1.actor.receivedmessages_set.count(), 1)
        self.assertTrue(farmer2.actor.receivedmessages_set.count(), 1)
    
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
        rpiarea = utils.create_rpiarea("rpiarea")
        district = utils.create_district("district", rpiarea)
        market = utils.create_market("market", district)
        agent = utils.create_agent()
        
        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        price = 200
        
        offer = monitor.register_offer(market, agent, crop, unit, price)
        self.assertTrue(monitor.is_monitoring(market))
        self.assertIn(market, monitor.markets.all())
        self.assertIn(market.district.rpiarea, monitor.rpiareas.all())
        self.assertEquals(offer.price, 200.0)
        self.assertEquals(offer.crop, crop)
        self.assertEquals(offer.unit, unit)
        self.assertEquals(offer.agent, agent)
        self.assertEquals(offer.market, market)
        self.assertAlmostEqual(offer.created_at, datetime.now(),
            delta=timedelta(seconds=2))
    


class FarmerTestCase(TestCase):
    
    def test_farmer_creation(self):
        farmer = utils.create_farmer(name="joe") 
        self.assertEquals(farmer.actor.user.first_name, "joe")
        self.assertEquals(farmer.farmergroup.name, "farmer group")
        self.assertEquals(farmer.agents.count(), 0)
    
    def test_farmer_agent_link(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.farmergroup.district)
        agent = utils.create_agent()
        
        farmer.sells_at(market, agent)
        self.assertTrue(agent.is_selling_for(farmer, market))
        self.assertIn(market, agent.markets.all())
        self.assertIn(farmer, agent.farmers.all())
        self.assertIn(market, farmer.markets.all())
    
    def test_farmer_districts(self):
        rpiarea = utils.create_rpiarea("rpiarea")
        district1 = utils.create_district("district 1", rpiarea)
        market1 = utils.create_market("market 1", district1)
        
        district2 = utils.create_district("district 2", rpiarea)
        market2 = utils.create_market("market 2", district2)
        
        farmer = utils.create_farmer()
        agent1 = utils.create_agent("agent 1")
        agent2 = utils.create_agent("agent 2")
        
        farmer.sells_at(market1, agent1)
        farmer.sells_at(market2, agent2)
        
        self.assertEquals(farmer.districts().count(), 2)
        self.assertIn(district1, farmer.districts())
        self.assertIn(district2, farmer.districts())
    
    def test_farmer_grows_crops(self):
        farmer = utils.create_farmer()
        crop = utils.random_crop()
        farmer.grows_crop(crop)
        self.assertIn(crop, farmer.crops.all())
    
    def test_farmer_creation(self):
        district = utils.random_district()
        rpiarea = utils.create_rpiarea("rpiarea")
        zone = utils.create_zone("zone", rpiarea)
        village = utils.create_village("village", district)
        farmergroup = utils.create_farmergroup("farmer group", zone, district, village)
        farmer = Farmer.create('27761234567', 'first', 'last', farmergroup)
        self.assertEquals(farmer.actor.name, 'first last')
        self.assertEquals(farmer.actor.user.username, '27761234567')
