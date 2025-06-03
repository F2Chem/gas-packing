import datetime

from django.test import TestCase
from django.urls import reverse

from computers.models import *
from util.util import *
from computers.templatetags.computer_helpers import *



class HelperTests(TestCase):
    def setUp(self):
        pass


    def test_risk_matrix(self):
        s = risk_matrix()
        self.assertTrue(len(s) > 10)

