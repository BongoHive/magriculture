# Python
from datetime import datetime, timedelta
from StringIO import StringIO
from zipfile import ZipFile

# Django
from django.utils.translation import ugettext_lazy as _
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.utils import override_settings
from django.core import mail

# Project
from magriculture.fncs import tasks
from magriculture.fncs.tests import utils
from magriculture.fncs.models.props import Message
from magriculture.fncs.models.props import CropReceipt
from magriculture.fncs.tasks import export_transactions


def create_farmer_for_agent(agent, market, **kwargs):
    farmer = utils.create_farmer(**kwargs)
    farmer.operates_at(market, agent)
    return farmer

def create_random_farmers(amount, agent, market):
    for i in range(amount):
        yield create_farmer_for_agent(agent, market, msisdn=27731234567 + i)

class FNCSTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.pin = '1234'
        self.province = utils.create_province('test province')
        self.district = utils.create_district('test district', self.province)
        self.ward = utils.create_ward('test ward', self.district)
        self.market = utils.create_market('test market', self.district)

        self.agent = utils.create_agent()
        self.msisdn = self.agent.actor.user.username

        identity = self.agent.actor.get_identity(self.msisdn)
        identity.set_pin(self.pin)
        identity.save()

        self.login_url = '%s?next=%s' % (reverse('login'), reverse('fncs:home'))
        self.farmers = list(create_random_farmers(10, self.agent, self.market))
        self.farmer = self.farmers[0]

    def farmer_url(self, *args, **kwargs):
        return utils.farmer_url(self.farmer.pk, *args, **kwargs)

    def take_in(self, *args):
        return utils.take_in(self.market, self.agent, self.farmer, *args)

    def login(self):
        self.client.login(username=self.msisdn, password=self.pin)

    def logout(self):
        self.client.logout()


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

class TransactionExportTestCase(FNCSTestCase):

    def setUp(self):
        super(TransactionExportTestCase, self).setUp()
        self.test_msisdn = '27861234567'
        self.login()

        self.user = utils.create_generic_user()
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
        receipt = self.take_in(10, 'boxes', 'oranges')
        transactions = utils.sell(receipt, 10, 10)
        print transactions
        self.assertEqual(True, True)
        # export_transactions(field_names, labels, queryset, user)
        # [email] = mail.outbox
        # self.assertEqual(
        #     email.recipients(), [self.user_helper.get_django_user().email])
        # self.assertEqual("LimaLinks Transaction export snapshot", email.subject)
        # self.assertEqual("Please find the transactions attached.", email.body)
        # fp = self.get_zipfile_attachment(
        #     email, 'transactions-export.zip', 'transactions-export.csv')
        # reader = csv.DictReader(fp)
        # transaction_ids = [row['transaction_id'] for row in reader]
        # self.assertEqual(
        #     set(transaction_ids),
        #     set(transactions.keys()))
