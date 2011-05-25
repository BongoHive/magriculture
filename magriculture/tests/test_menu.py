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


        sc = MenuConsumer(None)
        sc.r_server.flushall()
        sc.set_yaml_template(test_yaml)

        sess = sc.get_session("456789")
        sess.get_decision_tree().echo_on()
        sess.get_decision_tree().get_data()
        print sess.get_decision_tree().dump_json_data()
        sess.get_decision_tree().start()
        sess.get_decision_tree().question()
        sess.save()
        sess = None
        # after persisting to redis, retrieve afresh
        sess = sc.get_session("456789")
        sess.get_decision_tree().answer(1)
        sess.get_decision_tree().question()
        sess.save()
        sess = None
        # after persisting to redis, retrieve afresh
        sess = sc.get_session("456789")
        sess.get_decision_tree().answer('milk')
        sess.get_decision_tree().question()
        sess.save()
        sess = None
        # after persisting to redis, retrieve afresh
        sess = sc.get_session("456789")
        sess.get_decision_tree().answer(42)
        sess.get_decision_tree().question()
        sess.save()
        sess = None
        # after persisting to redis, retrieve afresh
        sess = sc.get_session("456789")
        sess.get_decision_tree().answer(23)
        sess.get_decision_tree().question()
        sess.save()
        sess = None
        # after persisting to redis, retrieve afresh
        sess = sc.get_session("456789")
        sess.get_decision_tree().answer(3)
        sess.get_decision_tree().question()
        sess.save()
        sess = None
        # after persisting to redis, retrieve afresh
        sess = sc.get_session("456789")
        sess.get_decision_tree().answer("19/05/2011")
        print sc.post_back_json("456789")
        sess.get_decision_tree().finish()
        sess.save()
        sess = None


        print ""
        print sc.get_session("456789").get_decision_tree().dump_json_data()
        print sc.get_session("456789").get_decision_tree().serialize_to_json()


        #print "\n\n"
        #time.sleep(2)
