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
        market = utils.create_market("market", farmer.districts.all()[0])
        agent = utils.create_agent()

        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        amount = 10

        receipt = agent.take_in_crop(market, farmer, amount, unit, crop)

        self.assertEquals(list(market.crops()), [crop])
