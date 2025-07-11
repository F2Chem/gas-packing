from django.test import TestCase
from gas_filling.models import *
#import datetime


class OrderViewsTests(TestCase):


    def setUp(self):
        self.row = Order(customer='Test')
        self.row.save()

    
    def testList(self):
        url = '/gas_filling/orders/'

        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
    def testShow(self):
        url = f'/gas_filling/orders/{self.row.id}/' 

        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'].customer, 'Test')
        
