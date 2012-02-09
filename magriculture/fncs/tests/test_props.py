from django.test import TestCase
from django.contrib.auth.models import User
from magriculture.fncs.tests import utils
from magriculture.fncs.models import Transaction

class TransactionTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_price_history(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.farmergroup.district)
        agent = utils.create_agent()

        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        price = 20
        amount = 10

        for i in range(100):
            receipt = agent.take_in_crop(market, farmer, amount, unit, crop)
            transaction = agent.register_sale(receipt, amount, price)

        price_history = Transaction.price_history_for(market, crop, unit)
        self.assertEquals(list(price_history), [20.0] * 100)
