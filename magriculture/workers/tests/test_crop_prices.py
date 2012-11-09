"""Tests for magriculture.workers.crop_prices"""

import json
from twisted.trial import unittest
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web import http
from vumi.tests.utils import get_stubbed_worker, FakeRedis
from vumi.message import TransportUserMessage
from magriculture.workers.crop_prices import (Farmer, CropPriceModel,
                                              CropPriceWorker, FncsApi,
                                              MarketList, AllMarkets,
                                              MyMarkets, BestMarkets)


# Test data for farmers and prices

FARMERS = {
    '+27885557777': {
        "farmer_name": "Farmer Bob",
        "crops": [
            ["crop1", "Peas"],
            ["crop2", "Carrots"],
            ],
        "markets": [
            ["market1", "Kitwe"],
            ["market2", "Ndola"],
            ],
        },
    }

PRICES = {
    ("market1", "crop1", "unit1"): {
        "unit_name": "boxes",
        "prices": [1.2, 1.1, 1.5],
        },
    ("market1", "crop1", "unit2"): {
        "unit_name": "crates",
        "prices": [1.6, 1.7, 1.8],
        },
    }

HIGHEST_MARKETS = {
    "crop1": [
        ("market1", "Kitwe"),
        ("market2", "Ndola"),
        ],
    "crop2": [
        ("market2", "Ndola"),
        ],
    }

ALL_MARKETS = [
        ("market1", "Kitwe"),
        ("market2", "Ndola"),
        ("market3", "Masala"),
    ]


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
      * crops: list of [crop_id, crop_name] pairs
      * markets: list of [market_id, market_name] pairs
    """

    def __init__(self, farmers):
        Resource.__init__(self)
        self.farmers = farmers

    def get_data(self, request):
        msisdn = "+" + request.args["msisdn"][0]
        return self.farmers[msisdn]


class DummyPriceHistoryResource(DummyResourceBase):
    """Dummy implementation of the /price_history/ HTTP api.

    /v1/price_history?market=<id>&crop=<id>&limit=<id> maps
    to JSON with:

      * <unit_id>: dictionary containing:
        * 'unit_name': name of the unit
        * 'prices': list of float prices for this unit
    """
    def __init__(self, prices):
        Resource.__init__(self)
        self.prices = prices

    def get_data(self, request):
        market_id = request.args["market"][0]
        crop_id = request.args["crop"][0]
        limit = int(request.args.get("limit", [10])[0])
        price_data = {}
        for (market_id, crop_id, unit_id), value in self.prices.items():
            if market_id == market_id and crop_id == crop_id:
                price_data[unit_id] = {
                    "unit_name": value["unit_name"],
                    "prices": value["prices"][:limit],
                    }
        return price_data


class DummyHighestMarketsResource(DummyResourceBase):
    """Dummy implementation of the /highest_markets/ HTTP api.

    /v1/highest_markets?crop=<id>&limit=<id> maps to JSON with:

      * a list of [market_id, market_name] pairs
    """
    def __init__(self, highest_markets):
        Resource.__init__(self)
        self.highest_markets = highest_markets

    def get_data(self, request):
        crop_id = request.args["crop"][0]
        limit = int(request.args.get("limit", [10])[0])
        return self.highest_markets[crop_id][:limit]


class DummyAllMarketsResource(DummyResourceBase):
    """Dummy implementation of the /markets/ HTTP api.

    /v1/markets?limit=<id> maps to JSON with:

      * a list of [market_id, market_name] pairs
    """
    def __init__(self, markets):
        Resource.__init__(self)
        self.markets = markets

    def get_data(self, request):
        limit = int(request.args.get("limit", [10])[0])
        return self.markets[:limit]


class DummyFncsApiResource(Resource):
    def __init__(self, farmers, prices, highest_markets, all_markets):
        Resource.__init__(self)
        self.putChild('farmer', DummyFarmerResource(farmers))
        self.putChild('price_history', DummyPriceHistoryResource(prices))
        self.putChild('highest_markets',
                      DummyHighestMarketsResource(highest_markets))
        self.putChild('markets',
                      DummyAllMarketsResource(all_markets))


class TestFncsApi(unittest.TestCase):
    @inlineCallbacks
    def setUp(self):

        site_factory = Site(DummyFncsApiResource(FARMERS, PRICES,
                                                 HIGHEST_MARKETS,
                                                 ALL_MARKETS))
        self.server = yield reactor.listenTCP(0, site_factory)
        addr = self.server.getHost()
        self.api = FncsApi("http://%s:%s/" % (addr.host, addr.port))

    @inlineCallbacks
    def tearDown(self):
        yield self.server.loseConnection()

    @inlineCallbacks
    def test_get_farmer(self):
        farmer_id = "+27885557777"
        data = yield self.api.get_farmer(farmer_id)
        self.assertEqual(data, {
            "farmer_name": FARMERS[farmer_id]["farmer_name"],
            "crops": FARMERS[farmer_id]["crops"],
            "markets": FARMERS[farmer_id]["markets"],
            })

    @inlineCallbacks
    def test_get_price_history(self):
        data = yield self.api.get_price_history("market1", "crop1", 2)
        self.assertEqual(data, {
            "unit1": {
                "unit_name": "boxes",
                "prices": PRICES[("market1", "crop1", "unit1")]["prices"][:2],
                },
            "unit2": {
                "unit_name": "crates",
                "prices": PRICES[("market1", "crop1", "unit2")]["prices"][:2],
                },
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
        site_factory = Site(DummyFncsApiResource(FARMERS, PRICES,
                                                 HIGHEST_MARKETS,
                                                 ALL_MARKETS))
        server = yield reactor.listenTCP(0, site_factory)
        try:
            addr = server.getHost()
            api_url = "http://%s:%s/" % (addr.host, addr.port)
            api = FncsApi(api_url)
            farmer_id = "+27885557777"
            farmer = yield Farmer.from_user_id(farmer_id, api)
            self.assertEqual(farmer.user_id, "+27885557777")
            self.assertEqual(farmer.farmer_name, "Farmer Bob")
            self.assertEqual(farmer.crops, FARMERS[farmer_id]["crops"])
            self.assertEqual(farmer.markets, FARMERS[farmer_id]["markets"])
        finally:
            yield server.loseConnection()


class TestMarketList(unittest.TestCase):
    def test_format_name(self):
        markets = MarketList("Markets for %(crop)s")
        self.assertEqual(markets.format_name("beans"),
                         "Markets for beans")

    def test_market_list(self):
        markets = MarketList("Markets for %(crop)s")
        self.assertRaises(NotImplementedError, markets.market_list)


class TestAllMarkets(unittest.TestCase):

    class DummyApi(object):
        def get_markets(self, limit):
            markets = [("id%d" % i, "Market %d" % i) for i in range(5)]
            return markets[:limit]

    def test_market_list(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        api = self.DummyApi()
        markets = AllMarkets("All Markets", 2)
        self.assertEqual(markets.market_list(api, farmer, "crop1"),
                         [('id0', 'Market 0'), ('id1', 'Market 1')])


class TestMyMarkets(unittest.TestCase):
    def test_market_list(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        farmer.markets = [('id0', 'Market 0'), ('id1', 'Market 1')]
        api = object()
        markets = MyMarkets("My Markets")
        self.assertEqual(markets.market_list(api, farmer, "crop1"),
                         [('id0', 'Market 0'), ('id1', 'Market 1')])


class TestBestMarkets(unittest.TestCase):
    class DummyApi(object):
        def __init__(self):
            self._crop_ids = []

        def get_highest_markets(self, crop_id, limit):
            self._crop_ids.append(crop_id)
            markets = [("id%d" % i, "Market %d" % i) for i in range(5)]
            return markets[:limit]

    def test_market_list(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        api = self.DummyApi()
        markets = BestMarkets("All Markets", 2)
        self.assertEqual(markets.market_list(api, farmer, "crop1"),
                         [('id0', 'Market 0'), ('id1', 'Market 1')])
        self.assertEqual(api._crop_ids, ["crop1"])


class TestCropPriceModel(unittest.TestCase):
    @inlineCallbacks
    def setUp(self):
        site_factory = Site(DummyFncsApiResource(FARMERS, PRICES,
                                                 HIGHEST_MARKETS,
                                                 ALL_MARKETS))
        self.server = yield reactor.listenTCP(0, site_factory)
        addr = self.server.getHost()
        self.api = FncsApi("http://%s:%s/" % (addr.host, addr.port))

    @inlineCallbacks
    def tearDown(self):
        yield self.server.loseConnection()

    def test_serialize(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        model = CropPriceModel(CropPriceModel.START, farmer, 1, None)
        data = json.loads(model.serialize())
        self.assertEqual(data, {
            "state": CropPriceModel.START,
            "farmer": farmer.serialize(),
            "selected_crop": 1,
            "selected_market": None,
            "markets": None,
            })

    def test_unserialize(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        data = json.dumps({
            "state": CropPriceModel.SELECT_CROP,
            "farmer": farmer.serialize(),
            "selected_crop": 1,
            "selected_market": 2,
            "markets": [["market1", "Kitwe"]],
            })
        model = CropPriceModel.unserialize(data)
        self.assertEqual(model.state, CropPriceModel.SELECT_CROP)
        self.assertEqual(model.selected_crop, 1)
        self.assertEqual(model.selected_market, 2)
        self.assertEqual(model.markets, [["market1", "Kitwe"]])
        self.assertEqual(model.farmer.user_id, "fakeid1")
        self.assertEqual(model.farmer.farmer_name, "Farmer Bob")

    @inlineCallbacks
    def test_from_user_id(self):
        farmer_id = "+27885557777"
        model = yield CropPriceModel.from_user_id(farmer_id, self.api)
        self.assertEqual(model.state, CropPriceModel.START)
        self.assertEqual(model.selected_crop, None)
        self.assertEqual(model.selected_market, None)
        self.assertEqual(model.farmer.user_id, farmer_id)
        self.assertEqual(model.farmer.farmer_name,
                         FARMERS[farmer_id]["farmer_name"])
        self.assertEqual(model.farmer.crops, FARMERS[farmer_id]["crops"])
        self.assertEqual(model.farmer.markets, FARMERS[farmer_id]["markets"])

    @inlineCallbacks
    def test_process_event(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        farmer.add_crop("crop1", "Peas")
        farmer.add_market("market1", "Kitwe")
        model = CropPriceModel(CropPriceModel.START, farmer)

        text, continue_session = yield model.process_event(None, self.api)
        self.assertEqual(text, "Hi Farmer Bob.\nSelect a service:\n"
                         "1. Market prices")
        self.assertTrue(continue_session)

        text, continue_session = yield model.process_event("1", self.api)
        self.assertEqual(text, "Select a crop:\n1. Peas")
        self.assertTrue(continue_session)

        text, continue_session = yield model.process_event("1", self.api)
        self.assertEqual(text,
                         "Select which markets to view:\n"
                         "1. All markets\n"
                         "2. Best markets for Peas")
        self.assertTrue(continue_session)
        self.assertEqual(model.selected_crop, 0)

        text, continue_session = yield model.process_event("2", self.api)
        self.assertEqual(text, "Select a market:\n1. Kitwe\n2. Ndola")
        self.assertTrue(continue_session)
        self.assertEqual(model.markets, [["market1", "Kitwe"],
                                         ["market2", "Ndola"]])

        text, continue_session = yield model.process_event("1", self.api)
        self.assertEqual(text,
                         "Prices of Peas in Kitwe:\n"
                         "  boxes: 1.27\n"
                         "  crates: 1.70\n"
                         "Enter 1 for next market, 2 for previous market.\n"
                         "Enter 3 to exit.")
        self.assertTrue(continue_session)
        self.assertEqual(model.selected_market, 0)

        text, continue_session = yield model.process_event("3", self.api)
        self.assertEqual(text, "Goodbye!")
        self.assertFalse(continue_session)

    @inlineCallbacks
    def test_highest_markets(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        farmer.add_crop("crop1", "Peas")
        model = CropPriceModel(CropPriceModel.SELECT_MARKET_LIST, farmer,
                               selected_crop=0)

        text, continue_session = yield model.process_event("2", self.api)
        self.assertEqual(text,
                         "Select a market:\n1. Kitwe\n2. Ndola")
        self.assertTrue(continue_session)
        self.assertEqual(model.markets, [["market1", "Kitwe"],
                                         ["market2", "Ndola"]])

        text, continue_session = yield model.process_event("2", self.api)
        self.assertEqual(text,
                         "Prices of Peas in Ndola:\n"
                         "  boxes: 1.27\n"
                         "  crates: 1.70\n"
                         "Enter 1 for next market, 2 for previous market.\n"
                         "Enter 3 to exit.")
        self.assertTrue(continue_session)
        self.assertEqual(model.selected_market, 1)

    @inlineCallbacks
    def test_all_markets(self):
        farmer = Farmer("fakeid1", "Farmer Bob")
        farmer.add_crop("crop1", "Peas")
        model = CropPriceModel(CropPriceModel.SELECT_MARKET_LIST, farmer,
                               selected_crop=0)

        text, continue_session = yield model.process_event("1", self.api)
        self.assertEqual(text,
                         "Select a market:\n1. Kitwe\n2. Ndola\n3. Masala")
        self.assertTrue(continue_session)
        self.assertEqual(model.markets, [["market1", "Kitwe"],
                                         ["market2", "Ndola"],
                                         ["market3", "Masala"]])

        text, continue_session = yield model.process_event("2", self.api)
        self.assertEqual(text,
                         "Prices of Peas in Ndola:\n"
                         "  boxes: 1.27\n"
                         "  crates: 1.70\n"
                         "Enter 1 for next market, 2 for previous market.\n"
                         "Enter 3 to exit.")
        self.assertTrue(continue_session)
        self.assertEqual(model.selected_market, 1)


class TestCropPriceWorker(unittest.TestCase):

    timeout = 5

    @inlineCallbacks
    def setUp(self):
        self.transport_name = 'test_transport'
        site_factory = Site(DummyFncsApiResource(FARMERS, PRICES,
                                                 HIGHEST_MARKETS,
                                                 ALL_MARKETS))
        self.server = yield reactor.listenTCP(0, site_factory)
        addr = self.server.getHost()
        api_url = "http://%s:%s/" % (addr.host, addr.port)
        self.worker = get_stubbed_worker(CropPriceWorker, {
            'transport_name': self.transport_name,
            'worker_name': 'test_crop_prices',
            'api_url': api_url})
        self.broker = self.worker._amqp_client.broker
        yield self.worker.startWorker()
        self.fake_redis = FakeRedis()
        self.worker.session_manager.r_server = self.fake_redis

    @inlineCallbacks
    def tearDown(self):
        self.fake_redis.teardown()
        yield self.worker.stopWorker()
        yield self.server.loseConnection()

    # TODO: factor this out into a common application worker testing base class
    @inlineCallbacks
    def send(self, content, session_event=None, from_addr=None):
        if from_addr is None:
            from_addr = list(FARMERS.keys())[0]
        msg = TransportUserMessage(content=content,
                                   session_event=session_event,
                                   from_addr=from_addr, to_addr='+5678',
                                   transport_name=self.transport_name,
                                   transport_type='fake',
                                   transport_metadata={})
        self.broker.publish_message('vumi', '%s.inbound' % self.transport_name,
                                    msg)
        yield self.broker.kick_delivery()

    # TODO: factor this out into a common application worker testing base class
    @inlineCallbacks
    def recv(self, n=0):
        msgs = yield self.broker.wait_messages('vumi', '%s.outbound'
                                                % self.transport_name, n)

        def reply_code(msg):
            if msg['session_event'] == TransportUserMessage.SESSION_CLOSE:
                return 'end'
            return 'reply'

        returnValue([(reply_code(msg), msg['content']) for msg in msgs])

    @inlineCallbacks
    def test_session_new(self):
        yield self.send(None, TransportUserMessage.SESSION_NEW)
        [reply] = yield self.recv(1)
        self.assertEqual(reply[0], "reply")
        self.assertTrue(reply[1].startswith("Hi Farmer Bob"))

    @inlineCallbacks
    def test_session_resume(self):
        yield self.send(None, TransportUserMessage.SESSION_NEW)
        yield self.send("1")
        [_start, reply] = yield self.recv(1)
        self.assertEqual(reply[0], "reply")
        self.assertTrue(reply[1].startswith("Select a crop:"))

    @inlineCallbacks
    def test_session_close(self):
        yield self.send(None, TransportUserMessage.SESSION_CLOSE)
        replies = yield self.recv()
        self.assertEqual(replies, [])

    @inlineCallbacks
    def test_unknown_user_id(self):
        yield self.send(None, TransportUserMessage.SESSION_NEW,
                        from_addr="123")
        [reply] = yield self.recv(1)
        self.assertEqual(reply[0], "end")
        self.assertEqual(reply[1], "You are not registered.")
        [v_error, k_error] = self.flushLoggedErrors(ValueError, KeyError)
