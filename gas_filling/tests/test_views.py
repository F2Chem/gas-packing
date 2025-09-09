from django.test import TestCase
from gas_filling.models import *
#import datetime


class CylinderViewTests(TestCase):
    def setUp(self):
        self.cylinder = Cylinder.objects.create(id=108, barcodeid='Kyle81', tare = 50, test_date = date(2183, 1, 24))
        self.order = Order.objects.create(id=71, customer='Cal')
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)


    def testCylinderList(self):
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

    def testCylinderCreate(self):
        url = f'/gas_filling/cylinder/create/{self.cylinder.barcodeid}/{self.order_line.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)



class BatchViewTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=71, customer='Kyle')
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)
        self.cylinder = Cylinder.objects.create(id=102, barcodeid='Kyle81', tare = 12, test_date = date(2183, 1, 24))
        self.filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line)
        self.batch = Batch.objects.create(id=12, batch_num=47, parent_order=self.order, start_weight=50, end_weight=500)


    def testBatchList(self):
        url = '/gas_filling/batch/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('batches', response.context)

    def testNewBatch(self):
        url = f'/gas_filling/batch/new_batch/{self.filling.id}/{self.batch.batch_num}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['batch_num'], self.filling.batch_num)

    def testContinueFillingRedirectBatchNum(self):
        self.filling.batch_num = None
        self.filling.save()
        url = f'/gas_filling/filling/continue/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)



class OrderViewsTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=71, customer='Lara')
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)
        self.cylinder = Cylinder.objects.create(id=102, barcodeid='Kyle81', tare = 12, test_date = date(2183, 1, 24))
        self.filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line)
    

    def testOrderList(self):
        url = '/gas_filling/order/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def testOrderShow(self):
        url = f'/gas_filling/order/{self.order.id}/' 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'].customer, 'Lara')

    def testOrderEdit(self):
        url = f'/gas_filling/order/{self.order.id}/edit/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'].customer, 'Lara')

    def testOrderCreate(self):
        url = '/gas_filling/order/create/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def testOrderStatus(self):
        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], self.order)

    def testOrderStatusPostClose(self):
        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.post(url, {'action': 'close'})
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'CLOSED')

    def testOrderlineCreate(self):
        url = f'/gas_filling/order/new_orderline/{self.order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def testOrderlineEdit(self):
        url = f'/gas_filling/order/edit_orderline/{self.order_line.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], self.order)

    def testFillingBarcode(self):
        url = f'/gas_filling/filling/{self.order_line.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def testFillingBatch(self):
        url = f'/gas_filling/filling/batch/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

    def testFillingHeelWeight(self):
        url = f'/gas_filling/filling/heelweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

    def testFillingConnectionWeight(self):
        url = f'/gas_filling/filling/connectionweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

    def testFillingEndWeight(self):
        url = f'/gas_filling/filling/endweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

    def testFillingPulledWeight(self):
        url = f'/gas_filling/filling/pulledweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

    def testFillingShow(self):
        url = f'/gas_filling/filling/show/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

    def testContinueFillingRedirectHeel(self):
        self.filling.batch_num = 1
        self.filling.heel_weight = None
        self.filling.save()
        url = f'/gas_filling/filling/continue/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def testPdfCreate(self):
        url = '/gas_filling/pdfcreate/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

