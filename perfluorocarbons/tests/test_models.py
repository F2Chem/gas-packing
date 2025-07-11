import datetime

from django.test import TestCase
from django.urls import reverse

from ..models import *
#from utils import *
from templatetags.helpers import *






class PerfluorocarbonTests(TestCase):
    
    def test_create_perfluorocarbon(self):
        count = Perfluorocarbon.objects.all().count()
        pfc = Perfluorocarbon(name='Perfluorobutane')
        pfc.save()
        
        self.assertEqual(Perfluorocarbon.objects.all().count(), count + 1)
        
