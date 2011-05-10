from twisted.python import log
from twisted.python.log import logging
from twisted.internet.defer import inlineCallbacks, returnValue

from vumi.workers.session.worker import SessionConsumer, SessionPublisher, SessionWorker

class MenuConsumer(SessionConsumer):
    queue_name = "magri.inbound.lactation.default"
    routing_key = "magri.inbound.lactation.default"

class MenuPublisher(SessionPublisher):
    routing_key = "magri.outbound.lactation.default"

class MenuWorker(SessionWorker):
    @inlineCallbacks
    def startWorker(self):
        log.msg("Starting the MenuWorker")
        self.publisher = yield self.start_publisher(MenuPublisher)
        yield self.start_consumer(MenuConsumer, self.publisher)

    def stopWorker(self):
        log.msg("Stopping the MenuWorker")

