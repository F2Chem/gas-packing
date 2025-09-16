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

        self.filling1 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line1, end_weight=284, pulled_weight=284, final_weight=284)
        self.filling2 = Filling.objects.create(cylinder=self.cylinder2, order_line=self.order_line1, end_weight=931, pulled_weight=931, final_weight=931)
        self.filling3 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line1, end_weight=138, pulled_weight=138, final_weight=138)
        self.filling4 = Filling.objects.create(cylinder=self.cylinder2, order_line=self.order_line1, end_weight=461, pulled_weight=461, final_weight=461)
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
        self.order_line1 = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=5, cylinder_type="STANDARD", fill_weight=500)
        self.order_line2 = OrderLine.objects.create(id=12, order=self.order, line_number=2, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=6, cylinder_type="STILLAGE", fill_weight=500)
        self.order_line3 = OrderLine.objects.create(id=262, order=self.order, line_number=3, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=6, cylinder_type="STILLAGE", fill_weight=500)
        self.order_line4 = OrderLine.objects.create(id=325, order=self.order, line_number=4, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=2, cylinder_type="STANDARD", fill_weight=500)
        self.order_line5 = OrderLine.objects.create(id=210, order=self.order, line_number=5, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=5, cylinder_type="STANDARD", fill_weight=500)

        self.filling1 = Filling.objects.create(cylinder=self.cylinder1, order_line=self.order_line1, end_weight=284, pulled_weight=284, final_weight=284)
        self.filling2 = Filling.objects.create(cylinder=self.cylinder2, order_line=self.order_line1, end_weight=931, pulled_weight=931, final_weight=931)
        self.filling3 = Filling.objects.create(cylinder=self.cylinder3, order_line=self.order_line1, end_weight=138, pulled_weight=138, final_weight=138)
        self.filling4 = Filling.objects.create(cylinder=self.cylinder4, order_line=self.order_line1, end_weight=461, pulled_weight=461, final_weight=461)
        self.filling5 = Filling.objects.create(cylinder=self.cylinder5, order_line=self.order_line1, connection_weight = 52)

        self.filling6 = Filling.objects.create(cylinder=self.cylinder3, order_line=self.order_line2, end_weight=138, pulled_weight=138, final_weight=138)

        self.filling6 = Filling.objects.create(cylinder=self.cylinder3, order_line=self.order_line3, end_weight=138)

        self.filling6 = Filling.objects.create(cylinder=self.cylinder3, order_line=self.order_line4, end_weight=138, pulled_weight=138, final_weight=138)
        self.filling6 = Filling.objects.create(cylinder=self.cylinder3, order_line=self.order_line4, end_weight=138, pulled_weight=138, final_weight=138)

        self.filling6 = Filling.objects.create(cylinder=self.cylinder3, order_line=self.order_line5, end_weight=138, pulled_weight=138, final_weight=138)
        self.filling6 = Filling.objects.create(cylinder=self.cylinder3, order_line=self.order_line5, end_weight=138, pulled_weight=138, final_weight=138)

    def testCylindersFilled(self):
        self.assertEqual(self.order_line1.cylinders_filled, 4)
        self.assertEqual(self.order_line2.cylinders_filled, 1)
        self.assertEqual(self.order_line3.cylinders_filled, 0)
        self.assertEqual(self.order_line4.cylinders_filled, 2)
        self.assertEqual(self.order_line5.cylinders_filled, 2)

    def testCylindersSomewhatFilled(self):
        self.assertEqual(self.order_line1.cylinders_somewhat_filled, 5)
        self.assertEqual(self.order_line2.cylinders_somewhat_filled, 1)
        self.assertEqual(self.order_line3.cylinders_somewhat_filled, 1)
        self.assertEqual(self.order_line4.cylinders_somewhat_filled, 2)
        self.assertEqual(self.order_line5.cylinders_somewhat_filled, 2)
        
    def testAllFilled(self):
        self.assertEqual(self.order_line1.all_filled, False)
        self.assertEqual(self.order_line2.all_filled, True)
        self.assertEqual(self.order_line3.all_filled, False)
        self.assertEqual(self.order_line4.all_filled, True)
        self.assertEqual(self.order_line5.all_filled, False)

    def testAllSomewhatFilled(self):
        self.assertEqual(self.order_line1.all_somewhat_filled, True)
        self.assertEqual(self.order_line2.all_somewhat_filled, True)
        self.assertEqual(self.order_line3.all_somewhat_filled, True)
        self.assertEqual(self.order_line4.all_somewhat_filled, True)
        self.assertEqual(self.order_line5.all_somewhat_filled, False)



class FillingTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=91, customer='Bo')
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)
        self.cylinder = Cylinder.objects.create(id='1234567', barcodeid = '71l4r487', tare = 82, test_date = date(2183, 1, 24))
        self.filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line, start_weight=100, empty_weight=103, connection_weight=102, end_weight=284, pulled_weight=262, final_weight=262)
        self.filling2 = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line, start_weight=None, empty_weight=None, connection_weight=None, end_weight=None, pulled_weight=None)
        self.stillage1 = Stillage.objects.create(stillage_num=360, filling=self.filling, end_weight=1052, pulled_weight=1000)
        self.stillage2 = Stillage.objects.create(stillage_num=124, filling=self.filling, end_weight=1054, pulled_weight=1000)
        self.stillage3 = Stillage.objects.create(stillage_num=13, filling=self.filling2, end_weight=2098, pulled_weight=2050)
        self.stillage4 = Stillage.objects.create(stillage_num=25, filling=self.filling2, end_weight=3001, pulled_weight=2051)

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
        self.assertEqual(self.filling.recycle_weight, 184)
        self.assertEqual(self.filling2.recycle_weight, 0.0)

    def testPulledDiffWeight(self):
        self.assertEqual(self.filling.pulled_diff_weight, 22)
        self.assertEqual(self.filling2.pulled_diff_weight, 0.0)

    def testStillageFinishedEndWeight(self):
        self.assertEqual(Stillage.finished_end_weight(self.filling), 2106)
        self.assertEqual(Stillage.finished_end_weight(self.filling2), 5099)

    def testStillageFinishedPulledWeight(self):
        self.assertEqual(Stillage.finished_pulled_weight(self.filling), 2000)
        self.assertEqual(Stillage.finished_pulled_weight(self.filling2), 4101)



class BatchTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=91, customer='Bo')
        self.batch = Batch.objects.create(id=36, batch_num = 81, parent_order=self.order, start_weight=5000, end_weight=12)

    def testUsedWeight(self):
        self.assertEqual(self.batch.used_weight, 4988)



class RecycleTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=91, customer='Sailor Sloth')
        self.recycle = Recycle.objects.create(id=36, recycle_num = 81, parent_order=self.order, start_weight=12, end_weight=5000)

    def testRecycledWeight(self):
        self.assertEqual(self.recycle.recycled_weight, 4988)
