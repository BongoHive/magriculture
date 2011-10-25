"""Tests for magriculture.workers.crop_prices"""

import json
from twisted.trial import unittest
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web import http
from vumi.tests.utils import get_stubbed_worker
from magriculture.workers.crop_prices import CropPriceWorker


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


class TestCropPriceWorker(unittest.TestCase):

    FARMERS = {
        '+27885557777': {
            }
        }

    PRICES = {
        }

    @inlineCallbacks
    def setUp(self):
        self.transport_name = 'test_transport'
        site_factory = Site(DummyFncsApiResource(self.FARMERS, self.PRICES))
        self.server = yield reactor.listenTCP(0, site_factory)
        addr = self.server.getHost()
        api_url = "http://%s:%s/" % (addr.host, addr.port)
        self.worker = get_stubbed_worker(CropPriceWorker, {
            'transport_name': 'test',
            'api_url': api_url})
        yield self.worker.startWorker()

    @inlineCallbacks
    def tearDown(self):
        yield self.worker.stopWorker()
        yield self.server.loseConnection()

    def test_new_session(self):
        pass
