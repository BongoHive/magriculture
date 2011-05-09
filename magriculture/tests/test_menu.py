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
            url: 173.45.90.19/dis-uat/api/getFarmerDetails
            username: admin
            password: Admin1234
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
                english: "Thank you! Your milk collection
                was registered successfully."

        __update__:
            url: 173.45.90.19/dis-uat/api/addMilkCollections
            username: admin
            password: Admin1234
            param: result
        '''


        sc = MenuConsumer(None)
        sc.set_yaml_template(test_yaml)
        sess4 = sc.get_session("456789")
        dt4 = sess4.get_decision_tree()

        sc.gsdt("456789").echo_on()
        repr(sc.gsdt("456789").start())
        #repr(sc.gsdt("456789").question())
        #sc.gsdt("456789").answer(1)
        repr(sc.gsdt("456789").question())
        sc.gsdt("456789").answer(1)
        repr(sc.gsdt("456789").question())
        sc.gsdt("456789").answer(42)
        repr(sc.gsdt("456789").question())
        sc.gsdt("456789").answer(23)
        repr(sc.gsdt("456789").question())
        sc.gsdt("456789").answer(3)
        repr(sc.gsdt("456789").question())
        sc.gsdt("456789").answer("03/03/2011")
        repr(sc.gsdt("456789").finish())

        print ''
        print repr(dt4.get_data_source())
        print sess4.get_decision_tree().dump_json_data()




        #print "\n\n"
        #time.sleep(2)
