from django.test import TestCase
from django.contrib.auth.models import User
from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import Actor
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
    
    def test_farmer_creation(self):
        farmer = utils.create_farmer(name="joe") 
        self.assertEquals(farmer.actor.user.first_name, "joe")
        self.assertEquals(farmer.farmergroup.name, "farmer group")
        self.assertEquals(farmer.agents.count(), 0)
    
    def test_agent_creation(self):
        agent = utils.create_agent()
        self.assertEquals(agent.farmers.count(), 0)
        self.assertEquals(agent.markets.count(), 0)

    def test_farmer_agent_link(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.farmergroup.district)
        agent = utils.create_agent()

        farmer.sells_at(market, agent)
        self.assertTrue(agent.sells_for(farmer, market))
        self.assertIn(market, agent.markets.all())
        self.assertIn(farmer, agent.farmers.all())
        self.assertIn(market, farmer.markets.all())
    
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
    
    def test_agent_sale(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.farmergroup.district)
        agent = utils.create_agent()
        
        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        price = 20
        amount = 10
        
        transaction = agent.register_sale(market, farmer, crop, unit, price, amount)
        self.assertTrue(agent.sells_for(farmer, market))
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
