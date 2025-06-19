import datetime
import re

from django.test import TestCase
from django.urls import reverse

from gas_filling.models import *
from util.util import *
from templatetags.helpers import *

from django.utils import timezone
from datetime import datetime



class CylinderTests(TestCase):
    def setUp(self):
        Cylinder(id='1234567', barcodeid = '71l4r487', tare = 82, test_date = timezone.make_aware(datetime(2183, 1, 24))).save()
        Cylinder(id='7654321', barcodeid = 'ky17B031', tare = 57, test_date = timezone.make_aware(datetime(2025, 3, 24))).save()

    def test_outcome_all(self):
        Cylinder1 = Cylinder.objects.get(id=1234567)
        Cylinder2 = Cylinder.objects.get(id=7654321)
        self.assertEqual(Cylinder1.check_in_date(), True)
        self.assertEqual(Cylinder2.check_in_date(), False)
        self.assertEqual(Cylinder.barcode_search('71l4r487'), Cylinder1)
        self.assertEqual(Cylinder.barcode_search('ky17B031'), Cylinder2)
        self.assertEqual(Cylinder.barcode_search('FakeBarcode'), "barcode error")



class FillingTests(TestCase):
    def setUp(self):
        Filling(id='1234567', cylinder = '71l4r487', order = '28lrcl47', weight = 50, time_entered = timezone.make_aware(datetime(2025, 6, 19)), status = 0).save()
        Filling(id='7654321', cylinder = 'ky17B031', order = '91kyvk32', weight = 60, time_entered = timezone.make_aware(datetime(2025, 6, 16)), status = 3).save()

    def test_outcome_all(self):
        Filling1 = Filling.objects.get(id=1234567)
        Filling2 = Filling.objects.get(id=7654321)
        self.assertEqual(Filling1.filling_status(), 0)
        self.assertEqual(Filling2.filling_status(), 3)
        Filling1.update_status()
        Filling2.update_status()
        self.assertEqual(Filling1.filling_status(), 1)
        self.assertEqual(Filling2.filling_status(), 4)


