# Python
from datetime import datetime
import itertools
import random

# Django
from django.test import TestCase

# Project
from magriculture.fncs.tests import utils
from magriculture.fncs import tasks
from magriculture.fncs.models.props import CropReceipt, CROP_QUALITY_CHOICES

next_user_number = itertools.count().next

class TestTasksFunction(TestCase):
    def create_crop_reciept(self):
        data = {"crop": utils.create_crop("crop_%s" % next_user_number()),
            "unit": utils.create_crop_unit("unit_%s" % next_user_number()),
            "farmer": utils.create_farmer(),
            "agent": utils.create_agent(),
            "market": utils.create_market("market_%s" % next_user_number(), "" % next_user_number()),
            "quality": random.choice(CROP_QUALITY_CHOICES)[0],
            "amount": random.randint(10,100),
            "created_at": datetime.now()}

        crop_receipt, _ = CropReceipt.objects.get_or_create(**data)

    def test_query_function_works(self):
        result = tasks.query_crop_receipt_for_old_crops.delay()
