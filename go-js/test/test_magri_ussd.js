// Tests for magri-ussd.js

var assert = require("assert");
var vumigo = require("vumigo_v01");
var app = require("../lib/magri-ussd");
var test_utils = vumigo.test_utils;


describe("test menu worker", function() {
    var tester = new test_utils.ImTester(app.api, {
        max_response_length: 160
    });

    it("new users should see the select_service state", function () {
        tester.check_state({
            user: null,
            content: null,
            next_state: "select_service",
            response: "^Hi Farmer Bob."
        });
    });
    it("select_service state should respond", function() {
        tester.check_state({
            user: {current_state: "select_service"},
            content: null,
            next_state: "select_service",
            response: ("^Hi Farmer Bob.[^]" +
                       "Select a service:[^]" +
                       "1. Market prices$")
        });
    });
    it("select_crop should respond", function() {
        tester.check_state({
            user: {current_state: "select_crop"},
            content: null,
            next_state: "select_crop",
            response: ("^Select a crop:[^]" +
                       "1. Peas[^]" +
                       "2. Carrots$")
        });
    });
    it("select_market_list should respond", function() {
        tester.check_state({
            user: {
                current_state: "select_market_list",
                custom: {
                    chosen_crop_name: "Peas"
                }
            },
            content: null,
            next_state: "select_market_list",
            response: ("^Select which markets to view:[^]" +
                       "1. All markets[^]" +
                       "2. Best markets for Peas$")
        });
    });
    it("select_market should respond (best_markets)", function() {
        tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_crop: "crop1",
                    select_market_list: "best_markets"
                }
            },
            content: null,
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                       "1. Kitwe[^]" +
                       "2. Ndola$")
        });
    });
    it("select_market should respond (all_markets)", function() {
        tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_market_list: "all_markets"
                }
            },
            content: null,
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                       "1. Kitwe[^]" +
                       "2. Ndola[^]" +
                       "3. Masala$")
        });
    });

    // show_prices

    it("show_prices should to to end", function() {
        tester.check_state({
            user: {
                current_state: "show_prices",
                custom: {
                    chosen_markets: [
                        ["crop0", "Peas"],
                        ["crop1", "Beans"]
                    ]
                }
            },
            content: "3",
            next_state: "end",
            continue_session: false,
            response: ("^Goodbye!")
        });
    });
});


/* Python Tests

class TestFncsApi(unittest.TestCase):
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

*/