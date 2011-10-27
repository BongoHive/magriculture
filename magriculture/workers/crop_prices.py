# -*- test-case-name: magriculture.workers.tests.test_crop_prices -*-
# -*- encoding: utf-8 -*-

"""USSD menu allow farmers to compare crop prices."""

import json
from urllib import urlencode
from twisted.internet.defer import inlineCallbacks, returnValue
from vumi.application import ApplicationWorker, SessionManager
from vumi.utils import get_deploy_int, http_request


class FncsApi(object):
    """Simple wrapper around the FNCS HTTP API."""

    def __init__(self, api_url):
        self.api_url = api_url

    def get_page(self, route, **params):
        url = '%s%s?%s' % (self.api_url, route, urlencode(params))
        d = http_request(url, '', {
            'User-Agent': 'mAgriculture HTTP Request',
            }, method='GET')
        d.addCallback(json.loads)
        return d

    def get_farmer(self, user_id):
        return self.get_page("farmer", msisdn=user_id)

    def get_price_history(self, market_id, crop_id, limit):
        return self.get_page("price_history", market=market_id, crop=crop_id,
                             limit=limit)


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
    SELECT_CROP, SELECT_MARKET, SHOW_PRICES, END = STATES = (
        "select_crop", "select_market", "show_prices", "end")
    START = SELECT_CROP

    def __init__(self, state, farmer, selected_crop=None,
                 selected_market=None):
        assert state in self.STATES
        self.state = state
        self.farmer = farmer
        self.selected_crop = selected_crop
        self.selected_market = selected_market

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
            }
        return json.dumps(model_data)

    @classmethod
    def unserialize(cls, data):
        model_data = json.loads(data)
        farmer = Farmer.unserialize(model_data["farmer"])
        return cls(model_data["state"], farmer,
                   model_data["selected_crop"],
                   model_data["selected_market"])

    def get_choice(self, text, min_choice, max_choice):
        try:
            choice = int(text)
            if not (min_choice <= choice <= max_choice):
                choice = None
        except ValueError:
            choice = None
        return choice

    def handle_select_crop(self, text):
        choice = self.get_choice(text, 1, len(self.farmer.crops))
        if choice is None:
            return "Please enter the number of the crop."
        self.selected_crop = choice - 1
        self.state = self.SELECT_MARKET

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

    def handle_select_market(self, text):
        choice = self.get_choice(text, 1, len(self.farmer.markets))
        if choice is None:
            return "Please enter the number of a market."
        self.selected_market = choice - 1
        self.state = self.SHOW_PRICES

    def display_select_market(self, err, _api):
        template = (
            "%(err)s"
            "Select a market:\n"
            "%(markets)s")
        market_lines = []
        for i, (_id, market_name) in enumerate(self.farmer.markets):
            market_lines.append("%d. %s" % (i + 1, market_name))
        markets = "\n".join(market_lines)
        return template % {
            "err": err + "\n" if err is not None else "",
            "markets": markets,
            }

    def handle_show_prices(self, text):
        choice = self.get_choice(text, 1, 3)
        if choice is None:
            return "Invalid selection."
        if choice == 1:
            self.selected_market -= 1
            if self.selected_market < 0:
                self.selected_market = len(self.farmer.markets) - 1
        elif choice == 2:
            self.selected_market += 1
            if self.selected_market >= len(self.farmer.markets):
                self.selected_market = 0
        elif choice == 3:
            self.state = self.END

    @inlineCallbacks
    def display_show_prices(self, err, api):
        crop_id, crop_name = self.farmer.crops[self.selected_crop]
        market_id, market_name = self.farmer.markets[self.selected_market]
        prices = yield api.get_price_history(market_id, crop_id, limit=5)
        template = (
            "Prices of %(crop)s in %(market)s:\n"
            "%(err)s"
            "%(price_text)s"
            "Enter 1 for next market, 2 for previous market.\n"
            "Enter 3 to exit.")
        price_lines = []
        for unit_id in sorted(prices.keys()):
            unit_info = prices[unit_id]
            price_lines.append("Sold as %s:" % unit_info["unit_name"])
            for price in unit_info["prices"]:
                price_lines.append("  %.2f" % price)
        price_text = "\n".join(price_lines)
        returnValue(template % {
                "crop": crop_name,
                "market": market_name,
                "err": err + "\n" if err is not None else "",
                "price_text": price_text,
                })

    def display_end(self, err, api):
        return "Goodbye!"

    @inlineCallbacks
    def process_event(self, text, api):
        """Consume an input from the user and updated the model state.
        """
        handler = getattr(self, "handle_%s" % self.state)
        if text is not None:
            err = handler(text)
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
        self.session_manager = SessionManager(
                get_deploy_int(self._amqp_client.vhost),
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
        if session:
            model = CropPriceModel.unserialize(session["model_data"])
        else:
            session = self.session_manager.create_session(user_id)
            model = yield CropPriceModel.from_user_id(user_id, self.api)

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
