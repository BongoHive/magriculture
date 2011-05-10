import json

from twisted.python import log
from twisted.python.log import logging
from twisted.internet.defer import inlineCallbacks, returnValue

from vumi.workers.session.worker import SessionConsumer, SessionPublisher, SessionWorker
from vumi.message import Message


class MenuConsumer(SessionConsumer):
    queue_name = "xmpp.inbound.gtalk.vumi@praekeltfoundation.org"
    routing_key = "xmpp.inbound.gtalk.vumi@praekeltfoundation.org"
    test_yaml = '''
    __data__:
        url: 173.45.90.19/dis-uat/api/getFarmerDetails
        username: admin
        password: Admin1234
        params:
            - telNo
        json: >

    __start__:
        display:
            english: "Hello."
        next: farmers

    farmers:
        question:
            english: "Hi. There are multiple farmers with this phone number. Who are you?"
        options: name
        next: cows

    cows:
        question:
            english: "For which cow would you like to submit a milk collection?"
        options: name
        next: quantityMilked

    quantityMilked:
        question:
            english: "How much milk was collected?"
        validate: integer
        next: quantitySold

    quantitySold:
        question:
            english: "How much milk did you sell?"
        validate: integer
        next: milkTimestamp

    milkTimestamp:
        question:
            english: "When was this collection done?"
        options:
              - display:
                    english: "Today"
                default: today
                next: __finish__
              - display:
                    english: "Yesterday"
                default: yesterday
                next: __finish__
              - display:
                    english: "An earlier day"
                next:
                    question:
                        english: "Which day was it [dd/mm/yyyy]?"
                    validate: date
                    next: __finish__

    __finish__:
        display:
            english: "Thank you! Your milk collection was registered successfully."

    __post__:
        url: 173.45.90.19/dis-uat/api/addMilkCollections
        username: admin
        password: Admin1234
        params:
            - result
    '''


    def consume_message(self, message):
        response = ''
        if not self.yaml_template:
            self.set_yaml_template(self.test_yaml)
        recipient = message.payload['sender']
        if not self.gsdt("456789").is_started():
            self.gsdt("456789").start()
            response += self.gsdt("456789").question()
        else:
            self.gsdt("456789").answer(message.payload['message'])
            if not self.gsdt("456789").is_completed():
                response += self.gsdt("456789").question()
            response += self.gsdt("456789").finish() or ''
            if self.gsdt("456789").is_completed():
                del self.sessions["456789"]
        self.publisher.publish_message(Message(recipient=recipient, message=response))


class MenuPublisher(SessionPublisher):
    routing_key = "xmpp.outbound.gtalk.vumi@praekeltfoundation.org"


class MenuWorker(SessionWorker):
    @inlineCallbacks
    def startWorker(self):
        log.msg("Starting the MenuWorker")
        self.publisher = yield self.start_publisher(MenuPublisher)
        yield self.start_consumer(MenuConsumer, self.publisher)

    def stopWorker(self):
        log.msg("Stopping the MenuWorker")


#class MenuWorker(SessionWorker):
    #@inlineCallbacks
    #def startWorker(self):
        #log.msg("Starting the XMPPWorker config: %s" % self.config)
        ## create the publisher
        #self.publisher = yield self.publish_to('xmpp.outbound.gtalk.%s' %
                                                #self.config['username'])
        ## when it's done, create the consumer and pass it the publisher
        #self.consume("xmpp.inbound.gtalk.%s" % self.config['username'],
                        #self.consume_message)

    #def consume_message(self, message):
        #recipient = message.payload['sender']
        #message = "You said: %s " % message.payload['message']
        #self.publisher.publish_message(Message(recipient=recipient, message=message))

    #def stopWorker(self):
        #log.msg("Stopping the XMPPWorker")

