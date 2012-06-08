"""Tests for magriculture.fncs.api."""

import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from magriculture.fncs.tests import utils
from magriculture.fncs.models.props import Transaction


class ApiTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def create_price_history(self):
        farmer = utils.create_farmer()
        market = utils.create_market("market", farmer.farmergroup.district)
        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")

        amount, price = 10, 20
        agent = utils.create_agent()

        for i in range(100):
            receipt = agent.take_in_crop(market, farmer, amount, unit, crop)
            agent.register_sale(receipt, amount, price)

        return crop, market, unit

    def create_highest_markets(self, prices):
        farmer = utils.create_farmer()
        markets = [
            utils.create_market("market %d" % i, farmer.farmergroup.district)
            for i in range(len(prices))]
        crop = utils.create_crop("potatoes")
        unit = utils.create_crop_unit("boxes")
        agent = utils.create_agent()
        amount = 10

        for market, price in zip(markets, prices):
            for i in range(10):
                receipt = agent.take_in_crop(market, farmer, amount, unit,
                                             crop)
                agent.register_sale(receipt, amount, price)

        return crop, markets

    def create_farmer(self, msisdn):
        province = utils.create_province('province')
        district = utils.create_district('district', province)
        market = utils.create_market("market", district)
        agent = utils.create_agent(password='1234')
        farmer = utils.create_farmer(msisdn=msisdn)
        farmer.operates_at(market, agent)
        return farmer

    def test_get_farmer(self):
        farmer = self.create_farmer(msisdn="27761234567")
        response = self.client.get(reverse('fncs:api_get_farmer'), {
            'msisdn': farmer.actor.user.username,
            })
        self.assertEqual(response.status_code, 200)
        farmer_data = json.loads(response.content)
        self.assertEqual(farmer_data, {
            "farmer_name": farmer.actor.name,
            "crops": [[crop.pk, crop.name] for crop in farmer.crops.all()],
            "markets": [[market.pk, market.name]
                        for market in farmer.markets.all()],
            })

    def test_get_farmer_with_normalized_msisdn(self):
        farmer = self.create_farmer(msisdn="061234567")
        response = self.client.get(reverse('fncs:api_get_farmer'), {
            'msisdn': "26061234567",  # normalized msisdn
            })
        self.assertEqual(response.status_code, 200)
        farmer_data = json.loads(response.content)
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

    def test_get_highest_markets(self):
        crop, markets = self.create_highest_markets(prices=[50, 100, 200])
        response = self.client.get(reverse('fncs:api_get_highest_markets'), {
            'crop': crop.pk,
            })
        self.assertEqual(response.status_code, 200)
        highest_markets = json.loads(response.content)
        print "HM:", highest_markets
        self.assertEqual(highest_markets, [
            [market.pk, market.name] for market in markets
            ])

    def test_get_highest_markets_with_limit(self):
        crop, markets = self.create_highest_markets(prices=[50, 100, 200])
        response = self.client.get(reverse('fncs:api_get_highest_markets'), {
            'crop': crop.pk,
            'limit': '2',
            })
        self.assertEqual(response.status_code, 200)
        highest_markets = json.loads(response.content)
        self.assertEqual(highest_markets, [
            [market.pk, market.name] for market in markets[:2]
            ])
