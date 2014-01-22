# Python
from datetime import datetime, timedelta

# Django
from django.test import TestCase

# Project
from magriculture.fncs import tasks
from magriculture.fncs.tests import utils
from magriculture.fncs.models.props import Message
from magriculture.fncs.models.props import CropReceipt

from django.test.utils import override_settings


# Settings override to allows for exceptions to be caught and change the test runner
@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS = True,
                   CELERY_ALWAYS_EAGER = True,
                   TEST_RUNNER='djcelery.contrib.test_runner.CeleryTestSuiteRunner')
class TestTasksFunction(TestCase):
    def test_query_function_works(self):
        # Creating Crop Receipts
        days_4 = utils.create_crop_receipt(created_at=datetime.today() - timedelta(days=4))
        days_2 = utils.create_crop_receipt(created_at=datetime.today() - timedelta(days=2))

        crop_receipts = CropReceipt.objects.all()

        # Assert that all reconciled is false
        (self.assertEqual(obj.reconciled, False) for obj in crop_receipts)
        tasks.query_crop_receipt_for_old_crops.delay(3)

        days_4 = CropReceipt.objects.get(id=days_4.id)
        self.assertEqual(days_4.reconciled, True)

        days_2 = CropReceipt.objects.get(id=days_2.id)
        self.assertEqual(days_2.reconciled, False)

        # Getting and testing the messages
        message = Message.objects.all()
        self.assertEqual(message.count(), 1)

        crop = days_4.crop.name
        remaining = days_4.remaining_inventory()
        self.assertEqual(message[0].content,
                         "Sorry but %s of %s have not been sold" % (remaining, crop))
        self.assertEqual(message[0].recipient,
                         days_4.farmer.actor)
        self.assertEqual(message[0].sender,
                         days_4.agent.actor)

    def test_query_function_works_with_day_is_one(self):
        # Creating Crop Receipts
        days_4 = utils.create_crop_receipt(created_at=datetime.today() - timedelta(days=4))
        days_2 = utils.create_crop_receipt(created_at=datetime.today() - timedelta(days=2))

        crop_receipts = CropReceipt.objects.all()

        # Assert that all reconciled is false
        (self.assertEqual(obj.reconciled, False) for obj in crop_receipts)
        tasks.query_crop_receipt_for_old_crops.delay(1)

        days_4 = CropReceipt.objects.get(id=days_4.id)
        self.assertEqual(days_4.reconciled, True)

        days_2 = CropReceipt.objects.get(id=days_2.id)
        self.assertEqual(days_2.reconciled, True)

        # Getting and testing the messages
        message = Message.objects.all()
        self.assertEqual(message.count(), 2)


    def test_check_inventory_left_works(self):
        days_4 = utils.create_crop_receipt(created_at=datetime.today() - timedelta(days=4))
        self.assertEqual(days_4.reconciled, False)

        tasks.check_inventory_left(days_4)
        days_4 = CropReceipt.objects.get(id=days_4.id)
        self.assertEqual(days_4.reconciled, True)

        # Getting and testing the messages
        message = Message.objects.all()
        self.assertEqual(message.count(), 1)

        crop = days_4.crop.name
        # Not sure why the following is being cast into an integer in the message
        remaining = int(days_4.remaining_inventory())
        self.assertEqual(message[0].content,
                         "Sorry but %s of %s have not been sold" % (remaining, crop))
        self.assertEqual(message[0].recipient,
                         days_4.farmer.actor)
        self.assertEqual(message[0].sender,
                         days_4.agent.actor)
