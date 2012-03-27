# -*- test-case-name: magriculture.workers.tests.test_crop_prices -*-
# -*- encoding: utf-8 -*-

"""USSD menu allow farmers to compare crop prices."""

import json
from urllib import urlencode
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python import log
from vumi.application import ApplicationWorker, SessionManager
from vumi.utils import http_request


class FncsApi(object):
    """Simple wrapper around the FNCS HTTP API."""

    def __init__(self, api_url):
        self.api_url = api_url

    def get_page(self, route, **params):
        url = '%s%s?%s' % (self.api_url, route, urlencode(params))
        log.msg("Fetching url %r" % url)
        d = http_request(url, '', {
            'User-Agent': 'mAgriculture HTTP Request',
            }, method='GET')
        d.addCallback(json.loads)
        return d

    def get_farmer(self, user_id):
        return self.get_page("farmer", msisdn=user_id.lstrip('+'))

    def get_price_history(self, market_id, crop_id, limit):
        return self.get_page("price_history", market=market_id, crop=crop_id,
                             limit=limit)

    def get_highest_markets(self, crop_id, limit):
        return self.get_page("highest_markets", crop=crop_id, limit=limit)


class Farmer(object):
    def __init__(self, user_id, farmer_name):
        self.user_id = user_id
        self.farmer_name = farmer_name
        self.crops = []
        self.markets = []

    def add_crop(self, crop_id, crop_name):
        self.crops.append((crop_id, crop_name))

    def add_market(self, market_id, market_name):
        self.markets.append((market_id, market_name))

    @classmethod
    @inlineCallbacks
    def from_user_id(cls, user_id, api):
        data = yield api.get_farmer(user_id)
        farmer = cls(user_id, data["farmer_name"])
        farmer.crops.extend(data["crops"])
        farmer.markets.extend(data["markets"])
        returnValue(farmer)

    def serialize(self):
        data = {
            "user_id": self.user_id,
            "farmer_name": self.farmer_name,
            "crops": self.crops,
            "markets": self.markets,
            }
        return json.dumps(data)

    @classmethod
    def unserialize(cls, json_str):
        data = json.loads(json_str)
        farmer = cls(data["user_id"], data["farmer_name"])
        farmer.crops.extend(data["crops"])
        farmer.markets.extend(data["markets"])
        return farmer


class CropPriceModel(object):
    """A simple state model of the interaction with a farmer
    viewing crop prices.

    :type state: str
    :param state:
        One of the model state constants.
    :type farmer: Farmer
    :param farmer:
        Details of the farmer interacting with the model.
    :type selected_crop: int
    :param selected_crop:
        The item from farmer.crops selected by the user.
    :type selected_market: int
    :param selected_market:
        The item from farmer.markets selected by the user.
    """
    # states of the model
    SELECT_CROP = "select_crop"
    SELECT_MARKET_LIST = "select_market_list"
    SELECT_MARKET = "select_market"
    SHOW_PRICES = "show_prices"
    END = "end"
    STATES = (
        SELECT_CROP, SELECT_MARKET_LIST, SELECT_MARKET, SHOW_PRICES, END,
        )
    START = SELECT_CROP

    # market lists
    HIGHEST_MARKETS = "highest_markets"
    MY_MARKETS = "my_markets"
    MARKET_LISTS = (HIGHEST_MARKETS, MY_MARKETS)

    def __init__(self, state, farmer, selected_crop=None,
                 selected_market=None, markets=None):
        assert state in self.STATES
        self.state = state
        self.farmer = farmer
        self.selected_crop = selected_crop
        self.selected_market = selected_market
        self.markets = markets

    @classmethod
    @inlineCallbacks
    def from_user_id(cls, user_id, api):
        farmer = yield Farmer.from_user_id(user_id, api)
        model = cls(cls.START, farmer)
        returnValue(model)

    def serialize(self):
        model_data = {
            "state": self.state,
            "farmer": self.farmer.serialize(),
            "selected_crop": self.selected_crop,
            "selected_market": self.selected_market,
            "markets": self.markets,
            }
        return json.dumps(model_data)

    @classmethod
    def unserialize(cls, data):
        model_data = json.loads(data)
        farmer = Farmer.unserialize(model_data["farmer"])
        return cls(model_data["state"], farmer,
                   model_data["selected_crop"],
                   model_data["selected_market"],
                   model_data["markets"])

    def get_choice(self, text, min_choice, max_choice):
        try:
            choice = int(text)
            if not (min_choice <= choice <= max_choice):
                choice = None
        except ValueError:
            choice = None
        return choice

    def handle_select_crop(self, text, _api):
        choice = self.get_choice(text, 1, len(self.farmer.crops))
        if choice is None:
            return "Please enter the number of the crop."
        self.selected_crop = choice - 1
        self.state = self.SELECT_MARKET_LIST

    def display_select_crop(self, err, _api):
        template = (
            "Hi %(farmer_name)s.\n"
            "%(err)s"
            "Select a crop:\n"
            "%(crops)s")
        crop_lines = []
        for i, (_id, crop_name) in enumerate(self.farmer.crops):
            crop_lines.append("%d. %s" % (i + 1, crop_name))
        crops = "\n".join(crop_lines)
        return template % {
            "farmer_name": self.farmer.farmer_name,
            "err": err + "\n" if err is not None else "",
            "crops": crops,
            }

    @inlineCallbacks
    def handle_select_market_list(self, text, api):
        choice = self.get_choice(text, 1, 2)
        if choice is None:
            returnValue("Please select a list of markets.")
        if choice == 1:
            crop_id = self.farmer.crops[self.selected_crop][0]
            self.markets = yield api.get_highest_markets(crop_id, 5)
        else:
            self.markets = self.farmer.markets
        self.state = self.SELECT_MARKET

    def display_select_market_list(self, err, _api):
        template = (
            "%(err)s"
            "Select which markets to view:\n"
            "1. Highest markets for %(crop)s\n"
            "2. My markets\n"
            )
        return template % {
            "err": err + "\n" if err is not None else "",
            "crop": self.farmer.crops[self.selected_crop][1],
            }

    def handle_select_market(self, text, _api):
        choice = self.get_choice(text, 1, len(self.markets))
        if choice is None:
            return "Please enter the number of a market."
        self.selected_market = choice - 1
        self.state = self.SHOW_PRICES

    def display_select_market(self, err, api):
        template = (
            "%(err)s"
            "Select a market:\n"
            "%(markets)s")
        market_lines = []
        for i, (_id, market_name) in enumerate(self.markets):
            market_lines.append("%d. %s" % (i + 1, market_name))
        markets = "\n".join(market_lines)
        return template % {
            "err": err + "\n" if err is not None else "",
            "markets": markets,
            }

    def handle_show_prices(self, text, _api):
        choice = self.get_choice(text, 1, 3)
        if choice is None:
            return "Invalid selection."
        if choice == 1:
            self.selected_market -= 1
            if self.selected_market < 0:
                self.selected_market = len(self.markets) - 1
        elif choice == 2:
            self.selected_market += 1
            if self.selected_market >= len(self.markets):
                self.selected_market = 0
        elif choice == 3:
            self.state = self.END

    @inlineCallbacks
    def display_show_prices(self, err, api):
        crop_id, crop_name = self.farmer.crops[self.selected_crop]
        market_id, market_name = self.markets[self.selected_market]
        prices = yield api.get_price_history(market_id, crop_id, limit=5)
        next_prev = ("Enter 1 for next market, 2 for previous market.\n"
                     if len(self.markets) > 1 else "")
        template = (
            "Prices of %(crop)s in %(market)s:\n"
            "%(err)s"
            "%(price_text)s\n"
            "%(next_prev)s"
            "Enter 3 to exit.")
        price_lines = []
        for unit_id in sorted(prices.keys()):
            unit_info = prices[unit_id]
            unit_prices = unit_info["prices"]
            if unit_prices:
                avg_text = "%.2f" % (sum(unit_prices) / len(unit_prices))
            else:
                avg_text = "-"
            price_lines.append("  %s: %s" % (unit_info["unit_name"],
                                           avg_text))
        price_text = "\n".join(price_lines)
        returnValue(template % {
                "crop": crop_name,
                "market": market_name,
                "err": err + "\n" if err is not None else "",
                "price_text": price_text,
                "next_prev": next_prev,
                })

    def display_end(self, err, api):
        return "Goodbye!"

    @inlineCallbacks
    def process_event(self, text, api):
        """Consume an input from the user and updated the model state.
        """
        handler = getattr(self, "handle_%s" % self.state)
        if text is not None:
            err = yield handler(text, api)
        else:
            err = None
        display = getattr(self, "display_%s" % self.state)
        result_text = yield display(err, api)
        returnValue((result_text, self.state != self.END))


class CropPriceWorker(ApplicationWorker):
    """A worker that presents a USSD menu allowing farmers to
    view recent crop prices.

    Configuration parameters:

    :type transport_name: str
    :param transport_name:
        Name of the transport (or dispatcher) to receive messages from and
        send message to.
    :type worker_name: str
    :param worker_name:
        Name of the worker. Used as the redis key prefix.
    :type api_url: str
    :param api_url:
        The URL of the FNCS HTTP API.
    """

    MAX_SESSION_LENGTH = 3 * 60

    @inlineCallbacks
    def startWorker(self):
        self.worker_name = self.config['worker_name']
        self.r_config = self.config.get('redis_config', {})
        self.redis_db = int(self.r_config.get("db", 0))
        self.session_manager = SessionManager(
                self.redis_db,
                self.worker_name,
                max_session_length=self.MAX_SESSION_LENGTH)
        self.api = FncsApi(self.config['api_url'])

        yield super(CropPriceWorker, self).startWorker()

    @inlineCallbacks
    def stopWorker(self):
        yield self.session_manager.stop()
        yield super(CropPriceWorker, self).stopWorker()

    @inlineCallbacks
    def consume_user_message(self, msg):
        user_id = msg.user()
        session = self.session_manager.load_session(user_id)
        if not session:
            session = self.session_manager.create_session(user_id)
        if "model_data" in session:
            model = CropPriceModel.unserialize(session["model_data"])
        else:
            try:
                model = yield CropPriceModel.from_user_id(user_id, self.api)
            except Exception, e:
                log.err(e)
                self.reply_to(msg, "You are not registered.", False)
                return

        reply, continue_session = yield model.process_event(msg['content'],
                                                            self.api)
        session["model_data"] = model.serialize()

        if continue_session:
            self.session_manager.save_session(user_id, session)
        else:
            self.session_manager.clear_session(user_id)

        self.reply_to(msg, reply, continue_session)

    def close_session(self, msg):
        user_id = msg.user()
        self.session_manager.clear_session(user_id)
