"""Tests for magriculture.workers.crop_prices"""

import json
from twisted.trial import unittest
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web import http
from vumi.tests.utils import get_stubbed_worker
from magriculture.workers.crop_prices import (Farmer, CropPriceModel,
                                              CropPriceWorker, FncsApi)


# Test data for farmers and prices

FARMERS = {
    '+27885557777': {
        "farmer_name": "Farmer Bob",
        "crops": [],
        "markets": [],
        },
    }

PRICES = {
    ("market1", "crop1", "unit1"): [1.2, 1.1, 1.5],
    }


class DummyResourceBase(Resource):
    """Base class for dummy resources."""

    isLeaf = True

    def render_GET(self, request):
        json_data = self.get_data(request)
        request.setResponseCode(http.OK)
        request.setHeader("content-type", "application/json")
        return json.dumps(json_data)


class DummyFarmerResource(DummyResourceBase):
    """Dummy implementation of the /farmer/ HTTP api.

    /v1/farmer?msisdn=<MSISDN> maps to JSON with:

      * name: farmer's name
      * crops: list of crops of interest
      * markets: list of markets of interest
    """

    def __init__(self, farmers):
        Resource.__init__(self)
        self.farmers = farmers

    def get_data(self, request):
        msisdn = request.args["msisdn"][0]
        return self.farmers[msisdn]


class DummyPriceHistoryResource(DummyResourceBase):
    """Dummy implementation of the /price_history/ HTTP api.

    /v1/price_history?market=<id>&crop=<id>&unit=<id>&limit=<id> maps
    to JSON with:

      * prices: list of floats
    """
    def __init__(self, prices):
        Resource.__init__(self)
        self.prices = prices

    def get_data(self, request):
        market_id = request.args["market"][0]
        crop_id = request.args["crop"][0]
        unit_id = request.args["unit"][0]
        limit = int(request.args.get("limit", [10])[0])
        prices = self.prices[(market_id, crop_id, unit_id)]
        return {"prices": prices[:limit]}


class DummyFncsApiResource(Resource):
    def __init__(self, farmers, prices):
        Resource.__init__(self)
        self.putChild('farmer', DummyFarmerResource(farmers))
        self.putChild('price_history', DummyPriceHistoryResource(prices))


class TestFncsApi(unittest.TestCase):
    @inlineCallbacks
    def setUp(self):
        site_factory = Site(DummyFncsApiResource(FARMERS, PRICES))
        self.server = yield reactor.listenTCP(0, site_factory)
        addr = self.server.getHost()
        self.api = FncsApi("http://%s:%s/" % (addr.host, addr.port))

    @inlineCallbacks
    def tearDown(self):
        yield self.server.loseConnection()

    @inlineCallbacks
    def test_get_farmer(self):
        data = yield self.api.get_farmer("+27885557777")
        self.assertEqual(data, {
            "farmer_name": "Farmer Bob",
            "crops": [],
            "markets": [],
            })

    @inlineCallbacks
    def test_get_price_history(self):
        data = yield self.api.get_price_history("market1", "crop1", "unit1", 5)
        self.assertEqual(data, {
            "prices": PRICES[("market1", "crop1", "unit1")],
            })


class TestFarmer(unittest.TestCase):

    def test_serialize(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        farmer.crops.append(("cropid1", "Peas"))
        farmer.markets.append(("marketid1", "Small Town Market"))
        data = json.loads(farmer.serialize())
        self.assertEqual(data, {
            "user_id": "fakeid1",
            "farmer_name": "Farmer Bob",
            "crops": [["cropid1", "Peas"]],
            "markets": [["marketid1", "Small Town Market"]],
            })

    def test_unserialize(self):
        data = json.dumps({
            "user_id": "fakeid1",
            "farmer_name": "Farmer Bob",
            "crops": [["cropid1", "Peas"]],
            "markets": [["marketid1", "Small Town Market"]],
            })
        farmer = Farmer.unserialize(data)
        self.assertEqual(farmer.user_id, "fakeid1")
        self.assertEqual(farmer.farmer_name, "Farmer Bob")
        self.assertEqual(farmer.crops, [["cropid1", "Peas"]])
        self.assertEqual(farmer.markets, [["marketid1", "Small Town Market"]])

    @inlineCallbacks
    def test_from_user_id(self):
        site_factory = Site(DummyFncsApiResource(FARMERS, PRICES))
        server = yield reactor.listenTCP(0, site_factory)
        try:
            addr = server.getHost()
            api_url = "http://%s:%s/" % (addr.host, addr.port)
            api = FncsApi(api_url)
            farmer = yield Farmer.from_user_id("+27885557777", api)
            self.assertEqual(farmer.user_id, "+27885557777")
            self.assertEqual(farmer.farmer_name, "Farmer Bob")
            self.assertEqual(farmer.crops, [])
            self.assertEqual(farmer.markets, [])
        finally:
            yield server.loseConnection()


class TestCropPriceModel(unittest.TestCase):
    def test_serialize(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        model = CropPriceModel(CropPriceModel.START, farmer)
        data = json.loads(model.serialize())
        self.assertEqual(data, {
            "state": CropPriceModel.START,
            "farmer": farmer.serialize(),
            })

    def test_unserialize(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        data = json.dumps({
            "state": CropPriceModel.SELECT_CROP,
            "farmer": farmer.serialize(),
            })
        model = CropPriceModel.unserialize(data)
        self.assertEqual(model.state, CropPriceModel.SELECT_CROP)
        self.assertEqual(model.farmer.user_id, "fakeid1")
        self.assertEqual(model.farmer.farmer_name, "Farmer Bob")

    @inlineCallbacks
    def test_from_user_id(self):
        site_factory = Site(DummyFncsApiResource(FARMERS, PRICES))
        server = yield reactor.listenTCP(0, site_factory)
        try:
            addr = server.getHost()
            api_url = "http://%s:%s/" % (addr.host, addr.port)
            api = FncsApi(api_url)
            model = yield CropPriceModel.from_user_id("+27885557777", api)
            self.assertEqual(model.state, CropPriceModel.START)
            self.assertEqual(model.farmer.user_id, "+27885557777")
            self.assertEqual(model.farmer.farmer_name, "Farmer Bob")
            self.assertEqual(model.farmer.crops, [])
            self.assertEqual(model.farmer.markets, [])
        finally:
            yield server.loseConnection()


class TestCropPriceWorker(unittest.TestCase):

    @inlineCallbacks
    def setUp(self):
        self.transport_name = 'test_transport'
        site_factory = Site(DummyFncsApiResource(FARMERS, PRICES))
        self.server = yield reactor.listenTCP(0, site_factory)
        addr = self.server.getHost()
        api_url = "http://%s:%s/" % (addr.host, addr.port)
        self.worker = get_stubbed_worker(CropPriceWorker, {
            'transport_name': 'test',
            'worker_name': 'test_crop_prices',
            'api_url': api_url})
        yield self.worker.startWorker()

    @inlineCallbacks
    def tearDown(self):
        yield self.worker.stopWorker()
        yield self.server.loseConnection()

    def test_new_session(self):
        pass