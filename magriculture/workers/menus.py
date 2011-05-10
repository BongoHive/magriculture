import json

from twisted.python import log
from twisted.python.log import logging
from twisted.internet.defer import inlineCallbacks, returnValue

from vumi.workers.session.worker import SessionConsumer, SessionPublisher, SessionWorker
from vumi.message import Message


#class MenuConsumer(SessionConsumer):
    #queue_name = "xmpp.inbound.gtalk.vumi@praekeltfoundation.org"
    #routing_key = "xmpp.inbound.gtalk.vumi@praekeltfoundation.org"

    #def consume_message(self, message):
            #recipient = message.payload['sender']
            #message = "You said: %s " % message.payload['message']
            #self.publisher.publish_message(Message(recipient=recipient, message=message))


#class MenuPublisher(SessionPublisher):
    #routing_key = "xmpp.outbound.gtalk.vumi@praekeltfoundation.org"


#class MenuWorker(SessionWorker):
    #@inlineCallbacks
    #def startWorker(self):
        #log.msg("Starting the MenuWorker")
        #self.publisher = yield self.start_publisher(MenuPublisher)
        #yield self.start_consumer(MenuConsumer, self.publisher)

    #def stopWorker(self):
        #log.msg("Stopping the MenuWorker")


class MenuWorker(SessionWorker):
    @inlineCallbacks
    def startWorker(self):
        log.msg("Starting the XMPPWorker config: %s" % self.config)
        # create the publisher
        self.publisher = yield self.publish_to('xmpp.outbound.gtalk.%s' %
                                                self.config['username'])
        # when it's done, create the consumer and pass it the publisher
        self.consume("xmpp.inbound.gtalk.%s" % self.config['username'],
                        self.consume_message)

    def consume_message(self, message):
        recipient = message.payload['sender']
        message = "You said: %s " % message.payload['message']
        self.publisher.publish_message(Message(recipient=recipient, message=message))

    def stopWorker(self):
        log.msg("Stopping the XMPPWorker")

