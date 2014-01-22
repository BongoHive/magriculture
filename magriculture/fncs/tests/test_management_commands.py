# Django
from django.core.management import call_command
from django.test import TestCase

# Project
from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import Farmer
from magriculture.fncs.tests.test_views import FNCSTestCase

class TestCreateMarketDistrictCommand(TestCase):
    def setUp(self):
        self

    def test_convert_district_command(self):
        pass
