from django.test import TestCase
from gas_filling.models import *
#import datetime





class HomeViewTests(TestCase):
    def testHomeView(self):
        url = '/gas_filling/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)





class CylinderViewTests(TestCase):


    def setUp(self):
        self.cylinder = Cylinder.objects.create(barcodeid='Kyle81')


    def testCylinderList(self): ###
        url = '/gas_filling/cylinder/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


    def testCylinderShow(self):
        url = f'/gas_filling/cylinder/show/{self.cylinder.id}/'

        response = self.client.get(url)
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cylinder'].barcodeid, 'Kyle81')


    def testCylinderEdit(self):
        url = f'/gas_filling/cylinder/edit/{self.cylinder.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertEqual(form.instance.barcodeid, 'Kyle81')





class OrderViewsTests(TestCase):


    def setUp(self):
        self.order = Order.objects.create(customer='Test')
        self.filling = Filling.objects.create(cylinder='BO', order=self.order)

    
    def testOrderList(self):
        url = '/gas_filling/order/'

        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        

    def testOrderShow(self):
        url = f'/gas_filling/order/{self.order.id}/' 

        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'].customer, 'Test')


    def testOrderEdit(self):
        url = f'/gas_filling/order/{self.order.id}/edit/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'].customer, 'Test')


    def testOrderCreate(self):
        url = '/gas_filling/order/create/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


    def testFillingBarcode(self):
        url = f'/gas_filling/filling/{self.order.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


    def testFillingBatch(self):
        url = f'/gas_filling/filling/batch/{self.filling.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, 'BO')


    def testFillingTareWeight(self):
        url = f'/gas_filling/filling/tareweight/{self.filling.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, 'BO')

    
    def testFillingConnectionWeight(self):
        url = f'/gas_filling/filling/connectionweight/{self.filling.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, 'BO')


    def testFillingEndWeight(self):
        url = f'/gas_filling/filling/endweight/{self.filling.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, 'BO')


    def testFillingPulledWeight(self):
        url = f'/gas_filling/filling/pulledweight/{self.filling.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, 'BO')


    def testFillingShow(self):
        url = f'/gas_filling/filling/show/{self.filling.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, 'BO')
