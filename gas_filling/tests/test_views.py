from django.test import TestCase
from gas_filling.models import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now



class CylinderViewTests(TestCase):
    def setUp(self):
        self.cylinder = Cylinder.objects.create(id=108, barcodeid='Kyle81', tare = 50, test_date = date(2183, 1, 24))
        self.cylinder2 = Cylinder.objects.create(id=922, barcodeid='80Bo80', tare = 12, test_date = now())
        self.order = Order.objects.create(id=71, customer='Cal')
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)


    def testValidCylinderList(self):
        url = '/gas_filling/cylinder/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Valid")

    def testOutOfDateCylinderList(self):
        self.cylinder2.test_date = now().date() - relativedelta(years=6)
        self.cylinder2.save()
        url = f'/gas_filling/cylinder/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Expired")

    def testAlmostOutOfDateCylinderList(self):
        self.cylinder2.test_date = now().date() + relativedelta(months=2) - relativedelta(years=5)
        self.cylinder2.save()
        url = f'/gas_filling/cylinder/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Expiring Soon")



    def testValidCylinderShow(self):
        self.cylinder2.test_date = now()
        self.cylinder2.save()
        url = f'/gas_filling/cylinder/show/{self.cylinder2.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cylinder'].barcodeid, '80Bo80')
        self.assertContains(response, "Valid")

    def testOutOfDateCylinderShow(self):
        self.cylinder2.test_date = now().date() - relativedelta(years=6)
        self.cylinder2.save()
        url = f'/gas_filling/cylinder/show/{self.cylinder2.id}/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Expired")

    def testAlmostOutOfDateCylinderShow(self):
        self.cylinder2.test_date = now().date() + relativedelta(months=2) - relativedelta(years=5)
        self.cylinder2.save()
        url = f'/gas_filling/cylinder/show/{self.cylinder2.id}/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Expiring Soon")



    def testCylinderEdit(self):
        url = f'/gas_filling/cylinder/edit/{self.cylinder.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.instance.barcodeid, 'Kyle81')

        response = self.client.post(url, {"barcodeid": "Kyle81", "tare": 50, "test_date": "2183-01-24", "comments": "bo"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("cylinder/", response.url)



    def testCylinderCreate(self):
        url = f'/gas_filling/cylinder/create/{self.cylinder.barcodeid}/{self.order_line.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

        response = self.client.post(url, {"barcodeid": "BOBOBO", "tare": 50, "test_date": "2183-01-24", "comments": "bo"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/batch/", response.url)

    def testOutOfDateCylinderCreate(self):
        url = f'/gas_filling/cylinder/create/{self.cylinder.barcodeid}/{self.order_line.id}/'
        response = self.client.post(url, {"barcodeid": "LARA", "tare": 50, "test_date": "2000-06-17", "comments": "bo"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cylinder has expired!")

    def testAlmostOutOfDateCylinderCreate(self):
        url = f'/gas_filling/cylinder/create/{self.cylinder.barcodeid}/{self.order_line.id}/'
        response = self.client.post(url, {"barcodeid": "LARA", "tare": 50, "test_date": "2021-03-17", "comments": "bo"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cylinder approaching expiry")



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
        self.assertEqual(response.context['batch_num'], self.batch.batch_num)

        response = self.client.post(url, {"end_weight": 12, "start_weight": 1000})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/recycle/", response.url)



    def testContinueFillingRedirectBatchNum(self):
        self.filling.batch_id = None
        self.filling.save()
        url = f'/gas_filling/filling/continue/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)



class RecycleViewTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=71, customer='Kyle')
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)
        self.cylinder = Cylinder.objects.create(id=102, barcodeid='Kyle81', tare = 12, test_date = date(2183, 1, 24))
        self.filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line)
        self.recycle = Recycle.objects.create(id=12, recycle_num=47, parent_order=self.order, start_weight=500, end_weight=50)


    def testRecycleList(self):
        url = '/gas_filling/recycle/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('recycles', response.context)



    def testNewRecycle(self):
        url = f'/gas_filling/recycle/new_recycle/{self.filling.id}/{self.recycle.recycle_num}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recycle_num'], self.recycle.recycle_num)

        response = self.client.post(url, {"end_weight": 1000, "start_weight": 12})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/heelweight/", response.url)



    def testContinueFillingRedirectRecycleNum(self):
        self.filling.batch_id = 1
        self.filling.recycle_id = None
        self.filling.save()
        url = f'/gas_filling/filling/continue/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)



class OrderViewsTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(id=71, customer='Lara', status='CLOSED')
        self.order2 = Order.objects.create(id=12, customer='Bo', status='OPEN')
        self.order_line = OrderLine.objects.create(id=72, order=self.order, line_number=1, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500)
        self.order_line2 = OrderLine.objects.create(id=901, order=self.order, line_number=2, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=1, cylinder_type="STILLAGE", fill_weight=500, keep_heel = True)
        self.order_line3 = OrderLine.objects.create(id=149, order=self.order, line_number=3, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STANDARD", fill_weight=500, keep_heel = True)
        self.order_line4 = OrderLine.objects.create(id=10005, order=self.order, line_number=4, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=10, cylinder_type="STILLAGE", fill_weight=500, keep_heel = True)
        self.order_line5 = OrderLine.objects.create(id=845, order=self.order2, line_number=5, product="OCTAFLUOROPROPANE", cylinder_size=10, num_cylinders=3, cylinder_type="STILLAGE", fill_weight=500, keep_heel = True)
        self.cylinder = Cylinder.objects.create(id=102, barcodeid='Kyle81', tare = 12, test_date = date(2183, 1, 24))
        self.cylinder2 = Cylinder.objects.create(id=922, barcodeid='80Bo80', tare = 12, test_date = datetime.today() - relativedelta(years=6))
        self.cylinder3 = Cylinder.objects.create(id=347, barcodeid='37L4ra', tare = 12, test_date = datetime.today() + relativedelta(months=2) - relativedelta(years=5))
        self.batch = Batch.objects.create(id=12, batch_num=47, parent_order=self.order, product="OCTAFLUOROPROPANE", start_weight=50, end_weight=500)
        self.recycle = Recycle.objects.create(id=12, recycle_num=53, parent_order=self.order, product="OCTAFLUOROPROPANE", start_weight=500, end_weight=50)

        self.filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line)
        self.filling2 = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line2)
        self.filling3 = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line3)
        self.filling4 = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line4)
        self.filling5 = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line4, start_weight = 50, batch_id=self.batch.id, recycle_id=self.recycle.id)
        self.filling6 = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line5, start_weight = 50, end_weight = 5000, batch_id=self.batch.id, recycle_id=self.recycle.id)

        #self.stillage = Stillage.objects.create(stillage_num=360, filling=self.filling2, end_time=now(), pulled_time=None)
        #self.stillage2 = Stillage.objects.create(stillage_num=720, filling=self.filling2, end_time=now(), pulled_time=None)
        #self.stillage3 = Stillage.objects.create(stillage_num=446, filling=self.filling5, end_time=now(), pulled_time=now(), final_time=None)
        #self.stillage4 = Stillage.objects.create(stillage_num=12, filling=self.filling5, end_time=now(), pulled_time=now(), final_time=None)

    

    def testOrderList(self):
        url = '/gas_filling/order/?status=OPEN'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = '/gas_filling/order/?status=CLOSED'
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

        response = self.client.post(url, {"customer": "BO", "order_number": 1251, "packaging_instruction": "fast", "qc_instruction": "faster"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"order/", response.url)



    def testOrderCreate(self):
        url = '/gas_filling/order/create/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {"customer": "BO", "order_number": 1251, "packaging_instruction": "fast", "qc_instruction": "faster", "product": "OCTAFLUOROPROPANE", "cylinder_size": 10, "cylinder_type": "STANDARD", "fill_weight": 500, "num_cylinders": 3, "keep_heel": False})
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"order/", response.url)



    def testOrderStatus(self):
        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], self.order)



    def testOrderStatusPOSTOpenToClosed(self):
        self.order.status = 'OPEN'
        self.order.save()

        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.post(url, {
            "action": "any",
            "packer_comments": "",
            "analyst_comments": "",
            "import_certificate": "",
            "export_certificate": "",
            "transport_company": "",
        })
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'CLOSED')

    def testOrderStatusPOSTInProgressToPacked(self):
        self.order.status = 'IN_PROGRESS'
        self.order.save()

        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.post(url, {
            "action": "any",
            "packer_comments": "Packed well",
            "analyst_comments": "",
            "import_certificate": "",
            "export_certificate": "",
            "transport_company": "",
        })
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'PACKED')
        self.assertEqual(self.order.packer_comments, 'Packed well')

    def testOrderStatusPOSTPackedToPassed(self):
        self.order.status = 'PACKED'
        self.order.save()

        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.post(url, {
            "action": "any",
            "packer_comments": "",
            "analyst_comments": "All good",
            "import_certificate": "",
            "export_certificate": "",
            "transport_company": "",
        })
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'PASSED')
        self.assertEqual(self.order.analyst_comments, 'All good')

    def testOrderStatusPOSTFailedAction(self):
        self.order.status = 'PACKED'
        self.order.save()

        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.post(url, {
            "action": "failed",
            "packer_comments": "",
            "analyst_comments": "Failed QA",
            "import_certificate": "",
            "export_certificate": "",
            "transport_company": "",
        })
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'FAILED')
        self.assertEqual(self.order.analyst_comments, 'Failed QA')

    def testOrderStatusPOSTPassedToFinished(self):
        self.order.status = 'PASSED'
        self.order.save()

        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.post(url, {
            "action": "any",
            "packer_comments": "",
            "analyst_comments": "",
            "import_certificate": "123456",
            "export_certificate": "on",
            "transport_company": "",
        })
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'FINISHED')
        self.assertEqual(self.order.import_certificate, '123456')
        self.assertTrue(self.order.export_certificate)

    def testOrderStatusPOSTFinishedToDispatched(self):
        self.order.status = 'FINISHED'
        self.order.save()

        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.post(url, {
            "action": "any",
            "packer_comments": "",
            "analyst_comments": "",
            "import_certificate": "",
            "export_certificate": "",
            "transport_company": "Build-a-Bear Exports",
        })
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'DISPATCHED')
        self.assertEqual(self.order.transport_company, 'Build-a-Bear Exports')

    def testOrderStatusFAILEDToREWORKED(self):
        self.order.status = 'FAILED'
        self.order.save()

        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.post(url, {
            "action": "any",
            "packer_comments": "",
            "analyst_comments": "",
            "import_certificate": "",
            "export_certificate": "",
            "transport_company": "",
        })

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'REWORKED')

    def testOrderStatusWarningINPROGRESS(self):
        self.order.status = 'IN_PROGRESS'
        self.order.save()

        url = f'/gas_filling/order/{self.order.id}/status/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Warning: 0 /', response.context['warning'])



    def testOrderlineCreate(self):
        url = f'/gas_filling/order/new_orderline/{self.order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {"product": "OCTAFLUOROPROPANE", "cylinder_size": 10, "cylinder_type": "STANDARD", "fill_weight": 500, "num_cylinders": 3, "keep_heel": False})
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"order/", response.url)




    def testOrderlineEdit(self):
        url = f'/gas_filling/order/edit_orderline/{self.order_line.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], self.order)

        response = self.client.post(url, {"product": "OCTAFLUOROPROPANE", "cylinder_size": 10, "cylinder_type": "STANDARD", "fill_weight": 500, "num_cylinders": 3, "keep_heel": False})
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"order/", response.url)



    def testCorrectFillingBarcode(self):
        url = f'/gas_filling/filling/{self.order_line.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {"cylinder_id": "Kyle81"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/batch/", response.url)

    def testIncorrectFillingBarcode(self):
        url = f'/gas_filling/filling/{self.order_line.id}/'
        response = self.client.post(url, {"cylinder_id": "999999"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("cylinder/create", response.url)
        
    def testOutOfDateFillingBarcode(self):
        url = f'/gas_filling/filling/{self.order_line.id}/'
        response = self.client.post(url, {"cylinder_id": "80Bo80"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cylinder has expired!")

    def testAlmostOutOfDateFillingBarcode(self):
        url = f'/gas_filling/filling/{self.order_line.id}/'
        response = self.client.post(url, {"cylinder_id": "37L4ra"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cylinder approaching expiry")



    def testFillingBatch1(self):
        url = f'/gas_filling/filling/batch/{self.filling.id}/'
        
        # First time, ask for a batch number
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

    def testFillingBatch2(self):
        url = f'/gas_filling/filling/batch/{self.filling.id}/'
        # Second time, new batch numer given, so go to page asking for start wt
        response = self.client.post(url, {"batch_num": "48"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("batch/new_batch/", response.url)

    def testFillingBatch3(self):
        url = f'/gas_filling/filling/batch/{self.filling.id}/'
        # Third time, old batch given, so go on to recycle stuff
        prev_filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line, filling_number=2, batch_id=self.batch.id)

        response = self.client.post(url, {"batch_num": "47"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/recycle/", response.url)
        
        
        

    def testFillingNewBatch(self):
        url = f'/gas_filling/filling/batch/{self.filling.id}/'
        response = self.client.post(url, {"batch_num": "87"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("batch/new_batch/", response.url)



    def testFillingRecycle1(self):
        url = f'/gas_filling/filling/recycle/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)
        

    def testFillingRecycle2(self):
        url = f'/gas_filling/filling/recycle/{self.filling.id}/'
        prev_filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line, filling_number=2, recycle_id=self.recycle.id)

        response = self.client.post(url, {"recycle_num": "54"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("recycle/new_recycle", response.url)
        

    def testFillingRecycle3(self):
        url = f'/gas_filling/filling/recycle/{self.filling.id}/'
        prev_filling = Filling.objects.create(cylinder=self.cylinder, order_line=self.order_line, filling_number=2, recycle_id=self.recycle.id)

        response = self.client.post(url, {"recycle_num": "53"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/heelweight/", response.url)
        
        
        
        
        
        

    def testFillingNewRecycle(self):
        url = f'/gas_filling/filling/recycle/{self.filling.id}/'
        response = self.client.post(url, {"recycle_num": "87"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("recycle/new_recycle/", response.url)



    def testFillingHeelWeight(self):
        url = f'/gas_filling/filling/heelweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

        response = self.client.post(url, {"start_weight": "50"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/connectionweight/", response.url)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/connectionweight/", response.url)



    def testFillingHeelWeightB(self):
        url = f'/gas_filling/filling/heelweight_b/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

        response = self.client.post(url, {"empty_weight": "50"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/endweight/", response.url)

        url = f'/gas_filling/filling/heelweight_b/{self.filling2.id}/'
        response = self.client.post(url, {"empty_weight": "50"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/endweight/", response.url)




    def testFillingConnectionWeight(self):
        url = f'/gas_filling/filling/connectionweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

        response = self.client.post(url, {"connection_weight": "52"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/heelweight_b/", response.url)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/endweight/", response.url)

        url = f'/gas_filling/filling/connectionweight/{self.filling2.id}/'
        response = self.client.post(url, {"connection_weight": "52"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/heelweight_b", response.url)

        url = f'/gas_filling/filling/connectionweight/{self.filling3.id}/'
        response = self.client.post(url, {"connection_weight": "52"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/endweight/", response.url)




    def testFillingEndWeight(self):
        url = f'/gas_filling/filling/endweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

        response = self.client.post(url, {"end_weight": "5000"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/pulledweight/", response.url)

        url = f'/gas_filling/filling/endweight/{self.filling2.id}/'
        response = self.client.post(url, {"end_weight": "5000"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/pulledweight/", response.url)

        url = f'/gas_filling/filling/endweight/{self.filling4.id}/'
        response = self.client.post(url, {"end_weight": "5000"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/endweight/", response.url)



    def testFillingPulledWeight(self):
        url = f'/gas_filling/filling/pulledweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

        response = self.client.post(url, {"pulled_weight": "5000"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/finalweight/", response.url)

        url = f'/gas_filling/filling/pulledweight/{self.filling2.id}/'
        response = self.client.post(url, {"pulled_weight": "5000"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/finalweight/", response.url)

        #self.stillage2.pulled_time = now()
        #response = self.client.post(url, {"pulled_weight": "5000"})
        #self.assertEqual(response.status_code, 302)
        #self.assertIn("filling/finalweight/", response.url)



    def testFillingFinalWeight(self):
        url = f'/gas_filling/filling/finalweight/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)

        response = self.client.post(url, {"final_weight": "5000"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("gas_filling/filling/", response.url)

        url = f'/gas_filling/filling/finalweight/{self.filling5.id}/'
        response = self.client.post(url, {"final_weight": "5000"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/finalweight/", response.url)

        #self.stillage4.final_time = now()
        #response = self.client.post(url, {"final_weight": "5000"})
        #self.assertEqual(response.status_code, 302)
        #self.assertIn("gas_filling/order/", response.url)



    def testFillingShow(self):
        url = f'/gas_filling/filling/show/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filling'].cylinder, self.cylinder)



    def testContinueFillingRedirectHeel(self):
        self.filling.batch_id = 1
        self.filling.recycle_id = 1
        self.filling.heel_weight = None
        self.filling.save()
        url = f'/gas_filling/filling/continue/{self.filling.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/heelweight/", response.url)

    def testContinueFillingRedirectEndWeight(self):
        url = f'/gas_filling/filling/continue/{self.filling5.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("filling/endweight/", response.url)


    # this needs all fillings to have weights, batches, etc. set up 
    # As the method does not do anything use yet, seems no point testing it yet.
    #def testPdfCreate(self):
    #    url = '/gas_filling/pdfcreate/'
    #    response = self.client.get(url)
    #    self.assertEqual(response.status_code, 200)

