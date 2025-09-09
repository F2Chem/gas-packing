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

        self.order = Order.objects.create(id=36, customer="Lara")
        self.order_line1 = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)
        self.order_line2 = OrderLine.objects.create(id=96, order=self.order, line_number=2, product="OCTAFLUOROPROPANE", cylinder_size=6, num_cylinders=2, cylinder_type="STANDARD", fill_weight=350)

        self.filling1 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line1, end_weight=284, pulled_weight=284)
        self.filling2 = Filling.objects.create(cylinder=self.cylinder2, order_line=self.order_line1, end_weight=931, pulled_weight=931)
        self.filling3 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line1, end_weight=138, pulled_weight=138)
        self.filling4 = Filling.objects.create(cylinder=self.cylinder2, order_line=self.order_line1, end_weight=461, pulled_weight=461)
        self.filling5 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line1, connection_weight = 52)

    def testTotalFillWeight(self):
        self.assertEqual(self.order.total_fill_weight, 1600)

    def testTotalFills(self):
        self.assertEqual(self.order.total_fills, 4)
        
    def testTotalOrderLines(self):
        self.assertEqual(self.order.total_orderlines, 2)

    def testTargetFill(self):
        self.assertEqual(self.order.target_fill, 850)



class OrderLineTests(TestCase):
    def setUp(self):
        self.cylinder1 = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', tare=50, test_date = date(2183, 1, 24))
        self.cylinder2 = Cylinder.objects.create(id='7654321', barcodeid = 'ky17B031', tare = 57, test_date = date(2025, 3, 24))
        self.cylinder3 = Cylinder.objects.create(id='9876543', barcodeid = 'Cu771y87', tare = 12, test_date = date(2025, 3, 24))
        self.cylinder4 = Cylinder.objects.create(id='8231795', barcodeid = '16C41781', tare = 42, test_date = date(2025, 3, 24))
        self.cylinder5 = Cylinder.objects.create(id='9342682', barcodeid = '2H4RRy12', tare = 64, test_date = date(2025, 3, 24))

        self.order = Order.objects.create(id=36, customer="Lara")
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=5, cylinder_type="STANDARD", fill_weight=500)

        self.filling1 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line, end_weight=284, pulled_weight=284)
        self.filling2 = Filling.objects.create(cylinder=self.cylinder2, order_line=self.order_line, end_weight=931, pulled_weight=0)
        self.filling3 = Filling.objects.create(cylinder=self.cylinder3, order_line=self.order_line, end_weight=138, pulled_weight=138)
        self.filling4 = Filling.objects.create(cylinder=self.cylinder4, order_line=self.order_line, end_weight=461, pulled_weight=461)
        self.filling5 = Filling.objects.create(cylinder=self.cylinder5, order_line=self.order_line, connection_weight = 52)

    def testCylindersFilled(self):
        self.assertEqual(self.order_line.cylinders_filled(), 3)

    def testCylindersSomewhatFilled(self):
        self.assertEqual(self.order_line.cylinders_somewhat_filled(), 5)
        
    def testAllFilled(self):
        self.assertEqual(self.order_line.all_filled(), False)

    def testAllSomewhatFilled(self):
        self.assertEqual(self.order_line.all_somewhat_filled(), True)



class FillingTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=91, customer='Bo')
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)
        self.cylinder = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', tare = 82, test_date = date(2183, 1, 24))
        self.filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line, heel_weight=100, heel_weight_b=103, connection_weight=102, end_weight=284, pulled_weight=262)
        self.filling2 = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line, heel_weight=None, heel_weight_b=None, connection_weight=None, end_weight=None, pulled_weight=None)

    def testHeelWeight(self):
        self.assertEqual(self.filling.net_heel_weight, 18)
        self.assertEqual(self.filling2.net_heel_weight, 0.0)

    def testFillWeight(self):
        self.assertEqual(self.filling.fill_weight, 180)
        self.assertEqual(self.filling2.fill_weight, 0.0)

    def testTakenWeight(self):
        self.assertEqual(self.filling.taken_weight, 182)
        self.assertEqual(self.filling2.taken_weight, 0.0)

    def testRecycleWeight(self):
        self.assertEqual(self.filling.recycle_weight, 3)
        self.assertEqual(self.filling2.recycle_weight, 0.0)

    def testPulledDiffWeight(self):
        self.assertEqual(self.filling.pulled_diff_weight, 22)
        self.assertEqual(self.filling2.pulled_diff_weight, 0.0)



class BatchTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=91, customer='Bo')
        self.batch = Batch.objects.create(id=36, batch_num = 81, parent_order=self.order, start_weight=5000, end_weight=12)

    def testUsedWeight(self):
        self.assertEqual(self.batch.used_weight, 4988)
