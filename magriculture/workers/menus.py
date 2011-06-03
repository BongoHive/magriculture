import json
import re

from twisted.python import log
from twisted.python.log import logging
from twisted.internet.defer import inlineCallbacks, returnValue

from vumi.workers.session.worker import SessionConsumer, SessionPublisher, SessionWorker
from vumi.message import Message
from vumi.webapp.api import utils
import vumi.options


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
        sess = self.get_session(recipient)
        if not sess.get_decision_tree().is_started():
            sess.get_decision_tree().start()
            response += sess.get_decision_tree().question()
        else:
            sess.get_decision_tree().answer(message.payload['message'])
            if not sess.get_decision_tree().is_completed():
                response += sess.get_decision_tree().question()
            response += sess.get_decision_tree().finish() or ''
            if sess.get_decision_tree().is_completed():
                sess.delete()
        sess.save()
        self.publisher.publish_message(Message(recipient=recipient, message=response))


    def call_for_json(self, MSISDN):
        MSISDN = "456789"
        if self.data_url['url']:
            params = [(self.data_url['params'][0], str(MSISDN))]
            url = self.data_url['url']
            auth_string = ''
            if self.data_url['username']:
                auth_string += self.data_url['username']
                if self.data_url['password']:
                    auth_string += ":" + self.data_url['password']
                auth_string += "@"
            resp_url, resp = utils.callback("http://"+auth_string+url, params)
            return resp
        return None


class MenuPublisher(SessionPublisher):
    routing_key = "xmpp.outbound.gtalk.vumi@praekeltfoundation.org"


class MenuWorker(SessionWorker):
    @inlineCallbacks
    def startWorker(self):
        log.msg("Starting the MenuWorker")
        log.msg("vumi.options: %s" % (vumi.options.get()))
        self.publisher = yield self.start_publisher(MenuPublisher)
        yield self.start_consumer(MenuConsumer, self.publisher)

    def stopWorker(self):
        log.msg("Stopping the MenuWorker")



class CellulantMenuConsumer(MenuConsumer):
    queue_name = "ussd.inbound.cellulant.http"
    routing_key = "ussd.inbound.cellulant.http"

    def unpackMessage(self, message):
        ussd = re.search(
              '^(?P<SESSIONID>[^|]*)'
            +'\|(?P<NETWORKID>[^|]*)'
            +'\|(?P<MSISDN>[^|]*)'
            +'\|(?P<MESSAGE>[^|]*)'
            +'\|(?P<OPERATION>[^|]*)$',
            message.payload['message'])
        if ussd:
            return ussd.groupdict()
        else:
            return {}

    def packMessage(self,
            SESSIONID,
            NETWORKID,
            MSISDN,
            MESSAGE,
            OPERATION):
       return "%s|%s|%s|%s|%s" % (
            SESSIONID,
            NETWORKID,
            MSISDN,
            MESSAGE,
            OPERATION)


    def consume_message(self, message):
        ussd = self.unpackMessage(message)
        response = ''
        if not self.yaml_template:
            self.set_yaml_template(self.test_yaml)
        sess = self.get_session(ussd['SESSIONID'])
        if not sess.get_decision_tree().is_started():
            sess.get_decision_tree().start()
            response += sess.get_decision_tree().question()
            ussd['OPERATION'] = 'INV'
        else:
            sess.get_decision_tree().answer(ussd['MESSAGE'])
            if not sess.get_decision_tree().is_completed():
                response += sess.get_decision_tree().question()
                ussd['OPERATION'] = 'INV'
            response += sess.get_decision_tree().finish() or ''
            if sess.get_decision_tree().is_completed():
                sess.delete()
                ussd['OPERATION'] = 'END'
        sess.save()
        ussd['MESSAGE'] = response
        self.publisher.publish_message(Message(
            uuid=message.payload['uuid'],
            message=self.packMessage(**ussd)))


class CellulantMenuPublisher(SessionPublisher):
    routing_key = "ussd.outbound.cellulant.http"

class CellulantMenuWorker(SessionWorker):
    @inlineCallbacks
    def startWorker(self):
        log.msg("Starting the CellulantMenuWorker")
        log.msg("vumi.options: %s" % (vumi.options.get()))
        self.publisher = yield self.start_publisher(CellulantMenuPublisher)
        yield self.start_consumer(CellulantMenuConsumer, self.publisher)

    def stopWorker(self):
        log.msg("Stopping the MenuWorker")

