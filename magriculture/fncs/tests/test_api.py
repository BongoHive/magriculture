"""Tests for magriculture.fncs.api."""
# Python
import json

# Django
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

# Project
from magriculture.fncs.tests import utils
from magriculture.fncs.models.props import Transaction
from magriculture.fncs.models.actors import Actor, Farmer


# Third Party
from tastypie.test import ResourceTestCase

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
        agent = utils.create_agent()
        identity = agent.actor.get_identity(agent.actor.user.username)
        identity.set_pin('1234')
        identity.save()
        farmer = utils.create_farmer(msisdn=msisdn)
        farmer.operates_at(market, agent)
        return farmer

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

    def test_get_markets(self):
        _crop, markets = self.create_highest_markets(prices=[50, 100, 200])
        response = self.client.get(reverse('fncs:api_get_markets'), {})
        self.assertEqual(response.status_code, 200)
        all_markets = json.loads(response.content)
        self.assertEqual(all_markets, [
            [market.pk, market.name] for market in markets
            ])

    def test_get_markets_with_limit(self):
        _crop, markets = self.create_highest_markets(prices=[50, 100, 200])
        response = self.client.get(reverse('fncs:api_get_markets'), {
            'limit': '2',
            })
        self.assertEqual(response.status_code, 200)
        all_markets = json.loads(response.content)
        self.assertEqual(all_markets, [
            [market.pk, market.name] for market in markets[:2]
            ])

class TestCreateFarmerApi(ResourceTestCase):
    fixtures = ["test_province.json",
                "test_district.json",
                "test_ward.json",
                "test_crop_unit.json",
                "test_crop.json"]

    def test_user_end_point_exists(self):
        """
        Testing of the farmer Api actually exists
        """
        url = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'user',
                      'api_name': 'v1'})
        response = self.api_client.get(url)
        self.assertEqual("application/json", response["Content-Type"])
        self.assertEqual(response.status_code, 200)
        json_item = json.loads(response.content)
        self.assertIn("meta", json_item)
        self.assertIn("objects", json_item)

    def test_farmer_end_point_exists(self):
        """
        Testing of the farmer Api actually exists
        """
        url = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'farmer',
                      'api_name': 'v1'})
        response = self.api_client.get(url)
        self.assertEqual("application/json", response["Content-Type"])
        self.assertEqual(response.status_code, 200)
        json_item = json.loads(response.content)
        self.assertIn("meta", json_item)
        self.assertIn("objects", json_item)


    def test_get_ward(self):
        """
        Get a specific ward
        """
        url = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'ward',
                      'api_name': 'v1'})
        response = self.api_client.get("%s?name=test_ward" % url)
        self.assertEqual("application/json", response["Content-Type"])
        self.assertEqual(response.status_code, 200)
        json_item = json.loads(response.content)
        self.assertIn("meta", json_item)
        self.assertIn("objects", json_item)
        self.assertEqual("test_ward", json_item["objects"][0]["name"])
        self.assertEqual(len(json_item["objects"]), 1)


    def test_get_district(self):
        """
       Get a specific district
        """
        url = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'district',
                      'api_name': 'v1'})
        response = self.api_client.get("%s?name=Zambezi" % url)
        self.assertEqual("application/json", response["Content-Type"])
        self.assertEqual(response.status_code, 200)
        json_item = json.loads(response.content)
        self.assertIn("meta", json_item)
        self.assertIn("objects", json_item)
        self.assertEqual("Zambezi", json_item["objects"][0]["name"])
        self.assertEqual(len(json_item["objects"]), 1)

    def test_get_crop(self):
        """
        get a specific crop
        """
        url = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'crop',
                      'api_name': 'v1'})
        response = self.api_client.get("%s?name=Cassava" % url)
        self.assertEqual("application/json", response["Content-Type"])
        self.assertEqual(response.status_code, 200)
        json_item = json.loads(response.content)
        self.assertIn("meta", json_item)
        self.assertIn("objects", json_item)
        self.assertEqual("Cassava", json_item["objects"][0]["name"])
        self.assertEqual(len(json_item["objects"]), 1)


    def test_create_farmer(self):
        """
        Test the actual create farmer functionality works
        """
        # Creating the initial user
        user_data = {"username": "27721231234",
                     "first_name": "test_first_name",
                     "last_name": "test_last_name"}
        url = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'user',
                      'api_name': 'v1'})
        response = self.api_client.post(url, data=user_data, format="json")
        json_item_user = json.loads(response.content)
        self.assertEqual("test_first_name", json_item_user["first_name"])
        self.assertEqual("test_last_name", json_item_user["last_name"])
        self.assertEqual("27721231234", json_item_user["username"])
        self.assertNotIn("password", json_item_user)
        self.assertNotIn("is_active", json_item_user)
        self.assertNotIn("is_staff", json_item_user)
        self.assertNotIn("is_superuser", json_item_user)
        self.assertNotIn("date_joined", json_item_user)
        self.assertNotIn("last_login", json_item_user)

        # Test if User has been created
        created_user = User.objects.get(username="27721231234")
        self.assertEqual("test_first_name", created_user.first_name)
        self.assertEqual("test_last_name", created_user.last_name)
        self.assertEqual("27721231234", created_user.username)
        self.assertEqual(True, created_user.is_active)
        self.assertEqual(False, created_user.is_staff)
        self.assertEqual(False, created_user.is_superuser)
        self.assertEqual('!', created_user.password)

        # Test if Actor has been created
        created_actor = Actor.objects.get(user__username="27721231234")
        self.assertEqual(created_actor.name, "test_first_name test_last_name")

        # Get Ward
        url_ward = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'ward',
                      'api_name': 'v1'})
        response_ward = self.api_client.get("%s?name=test_ward" % url_ward)
        json_item_ward = json.loads(response_ward.content)
        self.assertEqual(1, len(json_item_ward["objects"]))

        # Get Crop
        url_crop = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'crop',
                      'api_name': 'v1'})
        response_crop = self.api_client.get("%s?name=Cassava" % url_crop)
        json_item_crop = json.loads(response_crop.content)
        self.assertEqual(1, len(json_item_crop["objects"]))

        # Get District
        url_district = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'district',
                      'api_name': 'v1'})
        response_district = self.api_client.get("%s?name=Zambezi" % url_district)
        json_item_district = json.loads(response_district.content)
        self.assertEqual(1, len(json_item_district["objects"]))

        # Get District
        url_actor = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'actor',
                      'api_name': 'v1'})
        response_actor = self.api_client.get("%s?user__username=27721231234" % url_actor)
        json_item_actor = json.loads(response_actor.content)
        self.assertEqual(1, len(json_item_actor["objects"]))

        farmer_data = {
                        "actor": "/api/v1/actor/%s/" % json_item_actor["objects"][0]["id"],
                        "agents": "",
                        "crops": ["/api/v1/crop/%s/" % json_item_crop["objects"][0]["id"]],
                        "districts": ["/api/v1/district/%s/" % json_item_district["objects"][0]["id"]],
                        "hh_id": "",
                        "id_number": "123456789",
                        "markets": "",
                        "participant_type": "",
                        "resource_uri": "",
                        "wards": ["/api/v1/actor/%s/" % json_item_ward["objects"][0]["id"]]
                    }

        url_farmer = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'farmer',
                      'api_name': 'v1'})
        response = self.api_client.post(url_farmer, data=farmer_data, format="json")
        json_item = json.loads(response.content)

        self.assertEqual("123456789", json_item["id_number"])
        self.assertEqual("27721231234", json_item["actor"]["user"]["username"])
        self.assertEqual("test_first_name", json_item["actor"]["user"]["first_name"])
        self.assertEqual("test_last_name", json_item["actor"]["user"]["last_name"])
        self.assertEqual("27721231234", json_item["actor"]["user"]["username"])

        self.assertEqual("Cassava", json_item["crops"][0]["name"])
        self.assertEqual(1, len(json_item["crops"]))

        self.assertEqual("test_ward", json_item["wards"][0]["name"])
        self.assertEqual(1, len(json_item["wards"]))

        self.assertEqual("Zambezi", json_item["districts"][0]["name"])
        self.assertEqual(1, len(json_item["districts"]))

        self.assertEqual("27721231234", json_item["actor"]['user']["username"])
        self.assertEqual("test_first_name test_last_name", json_item["actor"]["name"])


    def test_create_malicious_user(self):
        """
        Test the actual create farmer functionality works
        """
        # Creating the initial user
        user_data = {"username": "27721231234",
                     "first_name": "test_first_name",
                     "last_name": "test_last_name",
                     "is_staff": True,
                     "is_superuser": True}
        url = reverse('fncs:api_dispatch_list',
                      kwargs={'resource_name': 'user',
                      'api_name': 'v1'})
        response = self.api_client.post(url, data=user_data, format="json")
        json_item_user = json.loads(response.content)
        self.assertEqual("test_first_name", json_item_user["first_name"])
        self.assertEqual("test_last_name", json_item_user["last_name"])
        self.assertEqual("27721231234", json_item_user["username"])
        self.assertNotIn("password", json_item_user)
        self.assertNotIn("is_active", json_item_user)
        self.assertNotIn("is_staff", json_item_user)
        self.assertNotIn("is_superuser", json_item_user)
        self.assertNotIn("date_joined", json_item_user)
        self.assertNotIn("last_login", json_item_user)

        # Test if User has been created
        created_user = User.objects.get(username="27721231234")
        self.assertEqual("test_first_name", created_user.first_name)
        self.assertEqual("test_last_name", created_user.last_name)
        self.assertEqual("27721231234", created_user.username)
        self.assertEqual(True, created_user.is_active)
        self.assertEqual(False, created_user.is_staff)
        self.assertEqual(False, created_user.is_superuser)
        self.assertEqual('!', created_user.password)

        # Test if Actor has been created
        created_actor = Actor.objects.get(user__username="27721231234")
        self.assertEqual(created_actor.name, "test_first_name test_last_name")
