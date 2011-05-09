import time
from twisted.trial.unittest import TestCase
from magriculture.workers.menus import MenuConsumer, MenuPublisher, MenuWorker

class MenuTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_menu(self):

        test_yaml = '''
        __data__:
            url:
            username:
            password:
            json: >
                {
                    "farmers": [
                        {
                            "name": "Richard",
                            "cows": [
                                {
                                    "name": "dairy",
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
                            "timestamp": "1294843761",
                            "farmerRegId": "frm1"
                        }
                    ],
                    "msisdn": "456789"
                }

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
                english: "Thank you! Your milk collection
                was registered successfully."
        '''


        sess_cons = MenuConsumer(None)
        sess_cons.set_yaml_template(test_yaml)
        sess4 = sess_cons.get_session("456789")
        dt4 = sess4.get_decision_tree()

        dt4.echo_on()
        repr(dt4.start())
        #repr(dt4.question())
        #dt4.answer(1)
        repr(dt4.question())
        dt4.answer(1)
        repr(dt4.question())
        dt4.answer(42)
        repr(dt4.question())
        dt4.answer(23)
        repr(dt4.question())
        dt4.answer(3)
        repr(dt4.question())
        dt4.answer("03/03/2011")
        repr(dt4.finish())

        print ''
        print repr(dt4.get_data_source())
        print sess4.get_decision_tree().dump_json_data()




        #print "\n\n"
        #time.sleep(2)
