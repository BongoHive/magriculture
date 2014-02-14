# Python
from datetime import datetime, timedelta
from StringIO import StringIO
from zipfile import ZipFile
import csv

# Django
from django.utils.translation import ugettext_lazy as _
from django.test import TestCase
# from django.core.urlresolvers import reverse
# from django.test.client import Client
from django.test.utils import override_settings
from django.core import mail

# Project
from magriculture.fncs import tasks
from magriculture.fncs.tests import utils
from magriculture.fncs.models.props import Message
from magriculture.fncs.models.props import CropReceipt
from magriculture.fncs.tasks import export_transactions


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
                         (_("Sorry but %(remaining)s %(units)s of %(crop)s have not been sold") %
                          {'remaining': remaining, 'units': days_4.unit.name, 'crop': crop}))
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
                         (_("Sorry but %(remaining)s %(units)s of %(crop)s have not been sold") %
                          {'remaining': remaining, 'units': days_4.unit.name, 'crop': crop}))
        self.assertEqual(message[0].recipient,
                         days_4.farmer.actor)
        self.assertEqual(message[0].sender,
                         days_4.agent.actor)

class TransactionExportTestCase(TestCase):

    def setUp(self):
    #     super(TransactionExportTestCase, self).setUp()
    #     self.test_msisdn = '27861234567'
    #     self.login()

        self.user = utils.create_generic_user()
        self.user.email = "test@example.com"
        self.user.is_superuser = True
        self.user.save()

    def get_attachment(self, email, file_name):
        for attachment in email.attachments:
            fn, attachment_content, mime_type = attachment
            if fn == file_name:
                return StringIO(attachment_content)

    def get_zipfile_attachment(
            self, email, attachment_file_name, zipfile_file_name):
        attachment = self.get_attachment(email, attachment_file_name)
        zipfile = ZipFile(attachment, 'r')
        return zipfile.open(zipfile_file_name, 'r')

    def test_export_conversation_messages_unsorted(self):
        receipt = utils.create_crop_receipt(amount=150)
        transaction = utils.create_transaction(receipt)
        transaction2 = utils.create_transaction(receipt)
        self.assertEqual(receipt.id, transaction.crop_receipt.id)
        field_names = ['id', 'crop_receipt__farmer__actor__name', 'crop_receipt__farmer__gender',
                    'created_at', 'crop_receipt__crop', 'crop_receipt__unit', 'amount',
                    'total', 'crop_receipt__market', 'crop_receipt__agent__actor__name',
                    'crop_receipt__agent__actor__gender']
        labels = ['TransactionID', 'Farmer Name', 'Gender', 'Transaction Date', 'Crop', 'Unit', 'No of Units',
                    'Total Price Achieved', 'Market', 'Agent', 'Agent Gender']
        queryset = [transaction, transaction2]
        export_transactions(field_names, labels, queryset, self.user)
        [email] = mail.outbox
        self.assertEqual(
            email.recipients(), [self.user.email])
        self.assertEqual("LimaLinks Transaction export snapshot", email.subject)
        self.assertEqual("Please find the transactions attached.", email.body)
        fp = self.get_zipfile_attachment(
            email, 'transactions-export.zip', 'transactions-export.csv')
        reader = csv.DictReader(fp)
        transaction_ids = [row['TransactionID'] for row in reader]
        self.assertEqual(
            set(transaction_ids),
            set(['1','2']))
