"""Tests for magriculture.workers.crop_prices"""

from twisted.trial import unittest
from vumi.tests.utils import get_stubbed_worker
from magriculture.workers.crop_prices import CropPriceWorker


class TestCropPriceWorker(unittest.TestCase):
    def setUp(self):
        self.transport_name = 'test_transport'
        self.worker = get_stubbed_worker(CropPriceWorker, {
            'transport_name': self.transport_name})
