"""Tests for magriculture.fncs.api."""

import json
from django.core.urlresolvers import reverse
from magriculture.fncs.tests.test_views import FNCSTestCase
from magriculture.fncs.tests import utils
from magriculture.fncs.models.props import Transaction


class ApiTestCase(FNCSTestCase):

    def create_price_history(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.farmergroup.district)
        agent = utils.create_agent()

        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        price = 20
        amount = 10

        for i in range(100):
            receipt = agent.take_in_crop(market, farmer, amount, unit, crop)
            agent.register_sale(receipt, amount, price)

        return crop, market, unit

    def test_get_farmer(self):
        farmer = self.farmers[0]
        response = self.client.get(reverse('fncs:api_get_farmer'), {
            'msisdn': farmer.actor.user.username,
            })
        self.assertEqual(response.status_code, 200)
        farmer_data = json.loads(response.content)
        print farmer_data
        self.assertEqual(farmer_data, {
            "farmer_name": farmer.actor.name,
            "crops": [[crop.pk, crop.name] for crop in farmer.crops.all()],
            "markets": [[market.pk, market.name]
                        for market in farmer.markets.all()],
            })

    def test_get_price_history(self):
        crop, market, unit = self.create_price_history()
        response = self.client.get(reverse('fncs:api_get_price_history'), {
            'crop': crop.pk,
            'market': market.pk,
            })
        self.assertEqual(response.status_code, 200)
        price_data = json.loads(response.content)
        self.assertEqual(price_data, {
            unicode(unit.pk): {
                "unit_name": "boxes",
                "prices": list(Transaction.price_history_for(
                                             market, crop, unit)[:10]),
                }
            })

    def test_get_price_history_with_limit(self):
        crop, market, unit = self.create_price_history()
        response = self.client.get(reverse('fncs:api_get_price_history'), {
            'crop': crop.pk,
            'market': market.pk,
            'limit': '2',
            })
        self.assertEqual(response.status_code, 200)
        price_data = json.loads(response.content)
        self.assertEqual(price_data, {
            unicode(unit.pk): {
                "unit_name": "boxes",
                "prices": list(Transaction.price_history_for(
                                             market, crop, unit)[:2]),
                }
            })
