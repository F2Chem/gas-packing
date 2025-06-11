import datetime
import re

from django.test import TestCase
from django.urls import reverse

from gas_filling.models import *
from util.util import *
from templatetags.helpers import *



class CylinderTestDate(TestCase):
    def setUp(self):
        Cylinder(id='1234567', barcodeid = '71l4r487', tare = 82, test_date = '2183-01-24').save()
        Cylinder(id='7654321', barcodeid = 'ky17B031', tare = 57, test_date = '2025-03-24').save()

    def test_outcome_all(self):
        Cylinder1 = Cylinder.objects.get(id=1234567)
        Cylinder2 = Cylinder.objects.get(id=7654321)
        self.assertEqual(Cylinder1.check_in_date(), True)
        self.assertEqual(Cylinder2.check_in_date(), False)
        self.assertEqual(Cylinder.barcode_search('71l4r487'), Cylinder1)
        self.assertEqual(Cylinder.barcode_search('ky17B031'), Cylinder2)
        self.assertEqual(Cylinder.barcode_search('FakeBarcode'), "barcode error")

