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
        self.cylinder1 = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', tare = 82, heel = 82, test_date = date(2183, 1, 24))
        self.cylinder2 = Cylinder.objects.create(id='7654321', barcodeid = 'ky17B031', tare = 57, heel = 57, test_date = date(2020, 3, 24))
        self.cylinder3 = Cylinder.objects.create(id='4236156', barcodeid = 'C4l4L0Y7', tare = 12, heel = 12, test_date = date(2020, 12, 12))

    def testCheckinDate(self):
        self.assertEqual(self.cylinder1.check_in_date(), 0)
        self.assertEqual(self.cylinder2.check_in_date(), 2)
        self.assertEqual(self.cylinder3.check_in_date(), 1)

    def testBarcodeSearch(self):
        self.assertAlmostEqual(Cylinder.barcode_search('71l4r487'), self.cylinder1)
        self.assertAlmostEqual(Cylinder.barcode_search('ky17B031'), self.cylinder2)
        self.assertEqual(Cylinder.barcode_search('FakeBarcode'), "barcode error")


class OrderTests(TestCase):
    def setUp(self):
        self.cylinder1 = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', tare=50, test_date = date(2183, 1, 24))
        self.cylinder2 = Cylinder.objects.create(id='7654321', barcodeid = 'ky17B031', tare = 57, test_date = date(2025, 3, 24))

        self.order = Order.objects.create()
        self.order_line = OrderLine.objects.create(order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, cylinder_type="STANDARD")
        self.filling1 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line, end_weight=284, pulled_weight=284) # 234
        self.filling2 = Filling.objects.create(cylinder=self.cylinder2, order_line=self.order_line, end_weight=931, pulled_weight=931) # 874
        self.filling3 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line, end_weight=138, pulled_weight=138) #88
        self.filling4 = Filling.objects.create(cylinder=self.cylinder2, order_line=self.order_line, end_weight=461, pulled_weight=461) # 404
        self.filling5 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line, connection_weight = 52)

    def testTotalFillWeight(self):
        self.assertEqual(self.order.total_fill_weight, 1600)

    def testTotalFills(self):
        self.assertEqual(self.order.total_fills, 4)


class FillingTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(customer='Test')
        self.order_line = OrderLine.objects.create(order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, cylinder_type="STANDARD")
        self.cylinder = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', tare = 82, test_date = date(2183, 1, 24))
        self.filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line, heel_weight= 100, end_weight=284, pulled_weight=284)

    def testHeelWeight(self):
        self.assertEqual(self.filling.net_heel_weight, 18)

    def testFillWeight(self):
        self.assertEqual(self.filling.fill_weight, 202)

