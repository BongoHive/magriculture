from django.test import TestCase
from django.contrib.auth.models import User
from magriculture.fncs.tests import utils
from magriculture.fncs.models import Transaction

class MarketTestCase(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_crops(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.farmergroup.district)
        agent = utils.create_agent()
        
        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        price = 20
        amount = 10
        
        agent.register_sale(market, farmer, crop, unit, price, amount)
        
        self.assertEquals(list(market.crops()), [crop])