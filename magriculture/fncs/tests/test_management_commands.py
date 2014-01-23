# Django
from django.core.management import call_command
from django.contrib.auth.models import User
from django.test import TestCase

# Project
from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import Farmer


class TestCreateMarketDistrictCommand(TestCase):
    def setUp(self):
        self.user_1, _ = User.objects.get_or_create(username="271231231",
                                                    first_name="user_first_1",
                                                    last_name="user_last_1")

        self.user_2, _ = User.objects.get_or_create(username="271231232",
                                                    first_name="user_first_2",
                                                    last_name="user_last_2")

        self.province = utils.create_province("province_name")
        self.district_1 = utils.create_district("district_1_name", self.province)
        self.district_2 = utils.create_district("district_2_name", self.province)
        self.market_1 = utils.create_market("market_1_name", self.district_1)
        self.market_2 = utils.create_market("market_1_name", self.district_2)
        self.farmer_1, _ = Farmer.objects.get_or_create(actor=self.user_1.get_profile())
        self.farmer_1.markets.add(self.market_1)
        self.farmer_1.markets.add(self.market_2)

        self.farmer_2, _ = Farmer.objects.get_or_create(actor=self.user_2.get_profile())
        self.farmer_2.markets.add(self.market_1)
        self.farmer_2.markets.add(self.market_2)
        self.farmer_2.districts.add(self.district_2)

    def test_convert_district_command(self):
        # Making sure that the farmer has no districts
        districts = [district for district in self.farmer_1.districts.all()]
        self.assertEquals([], districts)

        call_command('fncs_add_market_districts_for_farmers_with_no_districts')

        # Making sure farmers districts added corresponds to their markets
        farmer_1 = Farmer.objects.get(actor__user__username="271231231")
        farmer_1_districts = farmer_1.districts.values_list("name", flat=True)
        self.assertEqual(sorted(farmer_1_districts),
                         sorted([self.market_1.district.name, self.market_2.district.name]))

        # Making sure that if farmer has district, it remains as is
        farmer_2 = Farmer.objects.get(actor__user__username="271231232")
        farmer_2_districts = farmer_2.districts.values_list("name", flat=True)

        # If sorted not added below it fails even though both lists are equal (visually), not sure why.
        self.assertEqual(sorted(farmer_2_districts), sorted([self.district_2.name]))
