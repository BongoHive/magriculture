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

    def get_price_history(self, market_id, crop_id, unit_id, limit):
        return self.get_page("price_history", market=market_id, crop=crop_id,
                             unit=unit_id, limit=limit)


class Farmer(object):
    def __init__(self, user_id, farmer_name):
        self.user_id = user_id
        self.farmer_name = farmer_name
        self.crops = []
        self.markets = []

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
    :type user_id: str
    :param user_id:
        Unique id associated with the user.
    :type farmer_name:
    """
    # states of the model
    SELECT_CROP, SELECT_MARKETS, SHOW_PRICES = STATES = (
        "select_crop", "select_market", "show_prices")
    START = SELECT_CROP

    def __init__(self, state, farmer):
        assert state in self.STATES
        self.state = state
        self.farmer = farmer

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
            }
        return json.dumps(model_data)

    @classmethod
    def unserialize(cls, data):
        model_data = json.loads(data)
        state = model_data["state"]
        farmer = Farmer.unserialize(model_data["farmer"])
        return cls(state, farmer)

    def get_choice(self, text, min_choice, max_choice):
        try:
            choice = int(text)
            if not (min_choice <= choice <= max_choice):
                choice = None
        except ValueError:
            choice = None
        return choice

    def handle_select_crop(self, text):
        choice = self.get_choice(text, 1, len(self.crops))
        if choice is None:
            return "Please select a crop."
        self.selected_crop = choice
        self.state = self.SELECT_MARKET

    def display_select_crop(self):
        lines = [
            "Hi %s" % self.farmer_name,
            "Select crop to view prices for:",
            ]
        for i, (_id, crop_name) in enumerate(self.crops):
            lines.append("%d. %s" % (i, crop_name))
        return "\n".join(lines)

    def handle_select_market(self, text):
        choice = self.get_choice(text, 1, len(self.markets))
        if choice is None:
            return "Please select a market."
        self.selected_market = choice
        self.state = self.SHOW_PRICE

    def display_select_market(self):
        lines = [
            "Select market to view prices for:",
            ]
        for i, (_id, market_name) in enumerate(self.markets):
            lines.append("%d. %s" % (i, market_name))
        return "\n".join(lines)

    def handle_show_price(self, text):
        choice = self.get_choice(text, 1, 2)
        if choice is None:
            return "Invalid selection."
        self.state = self.START if choice == 1 else self.END

    def display_show_price(self):
        crop_id, crop_name = self.crops[self.selected_crop]
        market_id, market_name = self.markets[self.selected_market]
        return "TODO: show price for crop %s, market %s" % (
            crop_name, market_name)

    def process_event(self, text):
        """Consume an input from the user and updated the model state.
        """
        handler = getattr(self, "handle_%s" % self.state)
        err, new_state = handler(text)
        if new_state is not None:
            self.state = new_state
        display = getattr(self, "display_%s" % self.state)
        return display(), self.state != self.END


class CropPriceWorker(ApplicationWorker):

    MAX_SESSION_LENGTH = 3 * 60

    @inlineCallbacks
    def startWorker(self):
        self.worker_name = self.config['worker_name']
        self.session_manager = SessionManager(
                get_deploy_int(self._amqp_client.vhost),
                self.worker_name,
                max_session_length=self.MAX_SESSION_LENGTH)

        yield super(CropPriceWorker, self).startWorker()

    @inlineCallbacks
    def stopWorker(self):
        yield self.session_manager.stop()
        yield super(CropPriceWorker, self).stopWorker()

    def consume_user_message(self, msg):
        user_id = msg.user()
        session = self.session_manager.load_session(user_id)
        if session:
            model = CropPriceModel.unserialize(session["model_data"])
        else:
            session = self.session_manager.create_session(user_id)
            model = CropPriceModel.from_user_id(user_id)

        reply, continue_session = model.event(msg['content'])
        session["model_data"] = model.serialize()

        if continue_session:
            self.session_manager.save_session(user_id, session)
        else:
            self.session_manager.clear_session(user_id)

        self.reply_to(msg, reply, continue_session)
