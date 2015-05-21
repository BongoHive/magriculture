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

    def login(self, username, password):
        self.client.login(username=username, password=password)

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

    def add_crop_receipts(self, farmer, crops):
        for crop in crops:
            utils.create_crop_receipt(crop=crop, farmer=farmer)

    def add_markets(self, farmer, markets):
        district = farmer.districts.all()[0]
        for name in markets:
            market = utils.create_market(name, district)
            farmer.markets.add(market)

    def add_msisdns(self, farmer, msisdns):
        for msisdn in msisdns:
            farmer.actor.add_identity(msisdn)

    def farmer_export_csv(self, farmers):
        self.login('admin', 'password')
        action = {
            'action': 'custom_farmer_export_csv',
            '_selected_action': [unicode(f.pk) for f in farmers],
        }
        response = self.client.post(
            reverse('admin:fncs_farmer_changelist'), action)
        csv = response.content.splitlines()
        return csv

    def assert_farmer_csv(self, csv, rows):
        self.assertEqual(csv, [
            "FarmerID,ActorID,Farmer Name,First MSISDN,Number of MSISDNs,"
            "First Market,Number of Markets,Best CropID,Best Crop Name,"
            "Best Crop Amount"] + rows)

    def test_custom_farmer_export_simple(self):
        farmers = self.create_farmers()
        csv = self.farmer_export_csv(farmers)
        self.assert_farmer_csv(csv, [
            "3,5,name surname,27731234569,1,test market,1,,,0",
            "2,4,name surname,27731234568,1,test market,1,,,0",
            "1,3,name surname,27731234567,1,test market,1,,,0",
        ])

    def test_custom_farmer_export_with_crops(self):
        farmers = self.create_farmers()
        beans = utils.create_crop("beans")
        peas = utils.create_crop("peas")
        self.add_crop_receipts(farmers[0], [beans, beans, peas])
        self.add_crop_receipts(farmers[1], [peas, peas, beans])

        csv = self.farmer_export_csv(farmers)
        self.assert_farmer_csv(csv, [
            "3,5,name surname,27731234569,1,test market,1,,,0",
            "2,4,name surname,27731234568,1,test market,1,2,peas,2",
            "1,3,name surname,27731234567,1,test market,1,1,beans,2",
        ])

    def test_custom_farmer_export_with_multiple_msisdns(self):
        farmers = self.create_farmers()
        self.add_msisdns(farmers[0], ['+1234'])
        self.add_msisdns(farmers[1], ['+5678', '+9011'])

        csv = self.farmer_export_csv(farmers)
        self.assert_farmer_csv(csv, [
            "3,5,name surname,27731234569,1,test market,1,,,0",
            "2,4,name surname,+9011,3,test market,1,,,0",
            "1,3,name surname,+1234,2,test market,1,,,0",
        ])

    def test_custom_farmer_export_with_multiple_markets(self):
        farmers = self.create_farmers()
        self.add_markets(farmers[0], ['Kitwe'])
        self.add_markets(farmers[1], ['Chingola', 'Ndola'])

        csv = self.farmer_export_csv(farmers)
        self.assert_farmer_csv(csv, [
            "3,5,name surname,27731234569,1,test market,1,,,0",
            "2,4,name surname,27731234568,1,Chingola,3,,,0",
            "1,3,name surname,27731234567,1,Kitwe,2,,,0",
        ])
