"""Tests for magriculture.workers.crop_prices"""

from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks, returnValue
from vumi.tests.utils import get_stubbed_worker, FakeRedis
from vumi.message import TransportUserMessage
from magriculture.workers.menus import LactationWorker


class TestLactationWorker(unittest.TestCase):

    @inlineCallbacks
    def setUp(self):
        self.transport_name = 'test_transport'
        self.worker = get_stubbed_worker(LactationWorker, {
            'transport_name': self.transport_name,
            'worker_name': 'test_lactation',
            })
        self.broker = self.worker._amqp_client.broker
        yield self.worker.startWorker()
        self.fake_redis = FakeRedis()

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
                                    +"milk collection?\n1. dairy\n2. dell")

    @inlineCallbacks
    def test_session_continue_non_existant(self):
        yield self.send("1", TransportUserMessage.SESSION_RESUME)
        [reply] = yield self.recv(1)
        self.assertEqual(reply[0], "reply")
        self.assertEqual(reply[1], "For which cow would you like to submit a "
                                    +"milk collection?\n1. dairy\n2. dell")
        # TODO this should not pass
