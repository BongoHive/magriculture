""" Test for magriculture.fncs.admin. """

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from magriculture.fncs.tests import utils


class FarmerAdminTestCase(TestCase):
    def setUp(self):
        self.create_user('admin', 'password')
        self.client = Client()

    def create_user(self, username, password):
        User.objects.create_superuser(
            username, '%s@example.com' % username, password)

    def create_farmers(self):
        province = utils.create_province('test province')
        district = utils.create_district('test district', province)
        market = utils.create_market('test market', district)

        agent = utils.create_agent(msisdn="+260961234568")
        farmers = []
        for i in range(3):
            farmer = utils.create_farmer(msisdn=str(27731234567 + i))
            farmer.operates_at(market, agent)
            farmers.append(farmer)

        return farmers

    def login(self, username, password):
        self.client.login(username=username, password=password)

    def test_custom_farmer_export(self):
        self.login('admin', 'password')
        farmers = self.create_farmers()
        action = {
            'action': 'custom_farmer_export_csv',
            '_selected_action': [unicode(f.pk) for f in farmers],
        }
        response = self.client.post(
            reverse('admin:fncs_farmer_changelist'), action)
        csv = response.content.splitlines()
        self.assertEqual(csv, [
            "FarmerID,ActorID,Farmer Name,First MSISDN,Number of MSISDNs,"
            "First Market,Number of Markets,Best CropID,Best Crop Name,"
            "Best Crop Amount",
            "3,5,name surname,27731234569,1,test market,1,,,0",
            "2,4,name surname,27731234568,1,test market,1,,,0",
            "1,3,name surname,27731234567,1,test market,1,,,0",
        ])
