"""Tests for magriculture.workers.crop_prices"""

import re

from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks, returnValue
from vumi.tests.utils import get_stubbed_worker, FakeRedis
from vumi.message import TransportUserMessage
from magriculture.workers.menus import LactationWorker


class TestLactationWorker(unittest.TestCase):

    def replace_milktimestamp(self, string):
        newstring = re.sub(r'"milkTimestamp": "\d*"',
                            '"milkTimestamp": "0"',
                            string)
        return newstring

    def _post_result(self, result):
        print self
        self.result_list.append(result)

    def _call_for_json(self):
        print self
        return '''{
                    "farmers": [
                        {
                            "name":"David",
                            "cows": [
                                {
                                    "name":"dairy",
                                    "quantityMilked": 0,
                                    "milkTimestamp": 0,
                                    "cowRegId": "reg1",
                                    "quantitySold": 0
                                },
                                {
                                    "name": "dell",
                                    "quantityMilked": 0,
                                    "milkTimestamp": 0,
                                    "cowRegId": "reg2",
                                    "quantitySold": 0
                                }
                            ],
                            "timestamp": "1309852944",
                            "farmerRegId": "frm1"
                        }
                    ],
                    "msisdn": "456789"
                }'''

    @inlineCallbacks
    def setUp(self):
        self.transport_name = 'test_transport'
        LactationWorker.call_for_json = self._call_for_json
        LactationWorker.post_result = self._post_result
        self.worker = get_stubbed_worker(LactationWorker, {
            'transport_name': self.transport_name,
            'worker_name': 'test_lactation',
            })
        self.broker = self.worker._amqp_client.broker
        yield self.worker.startWorker()
        self.fake_redis = FakeRedis()
        self.result_list = []

    @inlineCallbacks
    def tearDown(self):
        self.fake_redis.teardown()
        yield self.worker.stopWorker()

    # TODO: factor this out into a common application worker testing base class
    @inlineCallbacks
    def send(self, content, session_event=None, from_addr=None):
        if from_addr is None:
            from_addr = "456789"
        msg = TransportUserMessage(content=content,
                                   session_event=session_event,
                                   from_addr=from_addr,
                                   to_addr='+5678',
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
        self.assertEqual(reply[1], "For which cow would you like to submit a "
                                    + "milk collection?\n1. dairy\n2. dell")

    @inlineCallbacks
    def test_session_complete_menu_traversal(self):
        yield self.send(None, TransportUserMessage.SESSION_NEW)
        yield self.send("1", TransportUserMessage.SESSION_RESUME)
        yield self.send("14", TransportUserMessage.SESSION_RESUME)
        yield self.send("10", TransportUserMessage.SESSION_RESUME)
        yield self.send("2", TransportUserMessage.SESSION_RESUME)
        replys = yield self.recv(1)
        self.assertEqual(len(replys), 5)
        self.assertEqual(replys[0][0], "reply")
        self.assertEqual(replys[0][1], "For which cow would you like to submit"
                                    + " a milk collection?\n1. dairy\n2. dell")
        self.assertEqual(replys[1][0], "reply")
        self.assertEqual(replys[1][1], "How much milk was collected?")
        self.assertEqual(replys[2][0], "reply")
        self.assertEqual(replys[2][1], "How much milk did you sell?")
        self.assertEqual(replys[3][0], "reply")
        self.assertEqual(replys[3][1], "When was this collection done?"
                            + "\n1. Today\n2. Yesterday\n3. An earlier day")
        self.assertEqual(replys[4][0], "end")
        self.assertEqual(replys[4][1], "Thank you! Your milk collection was"
                                    + " registered successfully.")
        self.assertEqual(self.replace_milktimestamp(self.result_list[0]),
                self.replace_milktimestamp(
                '{"msisdn": "456789", "farmers": '
                '[{"cows": [{"quantitySold": "10", '
                '"cowRegId": "reg1", "name": "dairy", '
                '"milkTimestamp": "1328824800", "quantityMilked": "14"}, '
                '{"quantitySold": 0, "cowRegId": "reg2", "name": "dell", '
                '"milkTimestamp": 0, "quantityMilked": 0}],'
                ' "timestamp": "1309852944", "farmerRegId": "frm1", '
                '"name": "David"}]}'
                ))

    @inlineCallbacks
    def test_session_complete_menu_traversal_with_bad_entries(self):
        yield self.send(None, TransportUserMessage.SESSION_NEW)
        yield self.send("3", TransportUserMessage.SESSION_RESUME)
        # '3' was out of range, so repeat with '1'
        yield self.send("1", TransportUserMessage.SESSION_RESUME)
        yield self.send("14", TransportUserMessage.SESSION_RESUME)
        yield self.send("very little", TransportUserMessage.SESSION_RESUME)
        # 'very litte' was not an integer so repeat with '0.5'
        yield self.send("0.5", TransportUserMessage.SESSION_RESUME)
        # '0.5' is of course still not an integer so repeat with '0'
        yield self.send("0", TransportUserMessage.SESSION_RESUME)
        yield self.send("2", TransportUserMessage.SESSION_RESUME)
        replys = yield self.recv(1)
        self.assertEqual(len(replys), 8)
        self.assertEqual(replys[0][0], "reply")
        self.assertEqual(replys[0][1], "For which cow would you like to submit"
                                    + " a milk collection?\n1. dairy\n2. dell")
        self.assertEqual(replys[1][0], "reply")
        self.assertEqual(replys[1][1], "For which cow would you like to submit"
                                    + " a milk collection?\n1. dairy\n2. dell")
        self.assertEqual(replys[2][0], "reply")
        self.assertEqual(replys[2][1], "How much milk was collected?")
        self.assertEqual(replys[3][0], "reply")
        self.assertEqual(replys[3][1], "How much milk did you sell?")
        self.assertEqual(replys[4][0], "reply")
        self.assertEqual(replys[4][1], "How much milk did you sell?")
        self.assertEqual(replys[5][0], "reply")
        self.assertEqual(replys[5][1], "How much milk did you sell?")
        self.assertEqual(replys[6][0], "reply")
        self.assertEqual(replys[6][1], "When was this collection done?"
                            + "\n1. Today\n2. Yesterday\n3. An earlier day")
        self.assertEqual(replys[7][0], "end")
        self.assertEqual(replys[7][1], "Thank you! Your milk collection was"
                                    + " registered successfully.")
        self.assertEqual(self.replace_milktimestamp(self.result_list[0]),
                self.replace_milktimestamp(
                '{"msisdn": "456789", "farmers": '
                '[{"cows": [{"quantitySold": "0", '
                '"cowRegId": "reg1", "name": "dairy", '
                '"milkTimestamp": "1328824800", "quantityMilked": "14"}, '
                '{"quantitySold": 0, "cowRegId": "reg2", "name": "dell", '
                '"milkTimestamp": 0, "quantityMilked": 0}],'
                ' "timestamp": "1309852944", "farmerRegId": "frm1", '
                '"name": "David"}]}'
                ))

    @inlineCallbacks
    def test_session_continue_non_existant(self):
        yield self.send("1", TransportUserMessage.SESSION_RESUME)
        [reply] = yield self.recv(1)
        self.assertEqual(reply[0], "reply")
        self.assertEqual(reply[1], "For which cow would you like to submit a "
                                    + "milk collection?\n1. dairy\n2. dell")
        # TODO this should not pass
