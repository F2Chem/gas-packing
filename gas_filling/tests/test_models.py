import datetime
import re

from django.test import TestCase
from django.urls import reverse

from gas_filling.models import *
from util.util import *
from templatetags.helpers import *

from django.utils import timezone
from datetime import date
from datetime import datetime



class CylinderTests(TestCase):
    def setUp(self):
        self.cylinder1 = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', heel = 82, test_date = date(2183, 1, 24))
        self.cylinder2 = Cylinder.objects.create(id='7654321', barcodeid = 'ky17B031', heel = 57, test_date = date(2025, 3, 24))

    def testCheckinDate(self):
        self.assertEqual(self.cylinder1.check_in_date(), True)
        self.assertEqual(self.cylinder2.check_in_date(), False)

    def testBarcodeSearch(self):
        self.assertAlmostEqual(Cylinder.barcode_search('71l4r487'), self.cylinder1)
        self.assertAlmostEqual(Cylinder.barcode_search('ky17B031'), self.cylinder2)
        self.assertEqual(Cylinder.barcode_search('FakeBarcode'), "barcode error")


class OrderTests(TestCase):
    def setUp(self):
        self.cylinder1 = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', heel = 82, test_date = date(2183, 1, 24))
        self.cylinder2 = Cylinder.objects.create(id='7654321', barcodeid = 'ky17B031', heel = 57, test_date = date(2025, 3, 24))

        self.order = Order.objects.create()
        self.filling1 = Filling.objects.create(cylinder=self.cylinder1, order=self.order, tare_weight=100, end_weight=284)
        self.filling2 = Filling.objects.create(cylinder=self.cylinder2, order=self.order, tare_weight=32, end_weight=931)
        self.filling3 = Filling.objects.create(cylinder=self.cylinder1, order=self.order, tare_weight=12, end_weight=138)
        self.filling4 = Filling.objects.create(cylinder=self.cylinder2, order=self.order, tare_weight=56, end_weight=461)

    def testTotalFillWeight(self):
        self.assertEqual(self.order.total_fill_weight, 1614)

    def testTotalFills(self):
        self.assertEqual(self.order.total_fills, 4)


class FillingTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(customer='Test')
        self.cylinder = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', heel = 82, test_date = date(2183, 1, 24))
        self.filling = Filling.objects.create(cylinder=self.cylinder, order=self.order, tare_weight=100, end_weight=284)

    def testHeelWeight(self):
        self.assertEqual(self.filling.heel_weight, 18)

    def testFillWeight(self):
        self.assertEqual(self.filling.fill_weight, 184)

