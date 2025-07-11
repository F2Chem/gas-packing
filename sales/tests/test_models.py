import datetime

from django.test import TestCase
from django.urls import reverse

from sales.models import *
from perfluorocarbons.models import *
#from utils import *
from templatetags.helpers import *





class CustomerTests(TestCase):
    def setUp(self):
        zone = Zone(name='EU', currency=2)
        zone.save()
        self.row = Customer(zone=zone, name="ACME CHemicals", currency=2, product_range=4, code="A001")
        self.row.save()


    def test_find_product_range_index(self):
        self.assertEqual(Customer.find_product_range_index('tg'), 4)
        self.assertEqual(Customer.find_product_range_index(3), 3)
        self.assertIsNone(Customer.find_product_range_index('xyz'))



    def test_create(self):
        zone = Zone(name='US', currency=1)
        zone.save()
        c = Customer.create(zone)
        self.assertEqual(c.currency, 1)
        #self.assertEqual(c.our_ref, 'A001/1')


    def test_currency_name(self):
        self.assertEqual(self.row.currency_name(), 'Euros')

    def test_show_money(self):
        self.assertEqual(self.row.show_money(123), '€1.23')
        self.assertEqual(self.row.show_money(100), '€1.00')
        self.assertEqual(self.row.show_money(0), '-')



    def test_product_name(self):
        pfc = Perfluorocarbon(name='Perfluorodecalin', tg_value='FLUTEC TG PFD')
        self.assertEqual(self.row.product_name(pfc), 'FLUTEC TG PFD')
        self.row.product_range = 0
        self.assertEqual(self.row.product_name(pfc), 'Perfluorodecalin')
        
        
    # also tests add_spec and remove_spec
    def test_list_specs_as_s(self):
        p = Product(name="Perfluoro-2-methylpentane", identifier="FLUTEC PP1", alt_names="FLUTEC PP1 HP,FLUTEC TG-PMP")
        p.save()
        spec1 = Spec(sample_log_product=p, name="QCS 12", product_name="FLUTEC TG PMCP")
        spec1.save()
        spec2 = Spec(sample_log_product=p, name="QCS 19", product_name="FLUTEC PP1C")
        spec2.save()
        self.assertEqual(self.row.specs.count(), 0)
        self.row.add_spec(spec1)
        self.row.add_spec(spec2)
        self.row.add_spec(spec2)
        self.row.add_spec(spec2)
        self.assertEqual(self.row.specs.count(), 2)
        self.assertEqual(self.row.list_specs_as_s(), 'FLUTEC TG PMCP (QCS 12), FLUTEC PP1C (QCS 19)')
        self.row.remove_spec(spec2)
        self.assertEqual(self.row.specs.count(), 1)
        self.row.remove_spec(spec2)
        self.assertEqual(self.row.specs.count(), 1)
        self.assertEqual(self.row.list_specs_as_s(), 'FLUTEC TG PMCP (QCS 12)')


    # also tests add_spec and remove_spec
    def test_assign_some_specs(self):
        p = Product(name="Perfluoro-2-methylpentane", identifier="FLUTEC PP1", alt_names="FLUTEC PP1 HP,FLUTEC TG-PMP")
        p.save()
        spec1 = Spec(sample_log_product=p, name="QCS 12", product_name="FLUTEC TG PMCP")
        spec1.save()
        spec2 = Spec(sample_log_product=p, name="QCS 19", product_name="FLUTEC PP1C")
        spec2.save()
        zone = Zone(name='US', currency=1)
        zone.save()

        c1 = Customer.create(zone)
        c1.product_range = 4  # tracers
        c1.save()
        c1.assign_some_specs()
        self.assertEqual(c1.list_specs_as_s(), 'FLUTEC TG PMCP (QCS 12)')

        c2 = Customer.create(zone)
        c2.product_range = 1  # PP
        c2.save()
        c2.assign_some_specs()
        self.assertEqual(c2.list_specs_as_s(), 'FLUTEC PP1C (QCS 19)')

        c3 = Customer.create(zone)
        c3.product_range = 0  # chem
        c3.save()
        c3.assign_some_specs()
        self.assertEqual(c3.list_specs_as_s(), '---None set---')




class FakeUser():
    username = 'fakeuser'


class OrderTests(TestCase):
    def setUp(self):
        zone = Zone(name='EU', currency=2)
        zone.save()
        cust = Customer(zone=zone, name="ACME CHemicals", currency=2, product_range=5, code="A001")
        cust.save()
        self.row = Order(customer=cust)
        self.row.save()





    def test_create(self):
        c = Customer.objects.get(name="ACME CHemicals")
        o = Order.create(c)
        o.save()
        self.assertEqual(o.our_ref, 'A001/1')
        o2 = Order.create(c)
        o2.save()
        self.assertEqual(o2.our_ref, 'A001/2')
        
        
    def test_status_various(self):
        self.row.set_status('Packing started')
        self.assertEqual(self.row.status_name(), 'Packing started')
        self.assertEqual(self.row.status_msg(), 'Click <i>Packing completed</i> to signal you have finished packing the order')


    def test_event(self):
        user = FakeUser()
        
        self.row.event('Packing completed', user)
            
        self.assertEqual(self.row.status_name(), 'Packing completed')
        #print(self.row.status_log)
        self.assertRegex(self.row.status_log, 'Packing completed by fakeuser')









        
class OrderLineTests(TestCase):
    def setUp(self):
        zone = Zone(name='US', currency=1)
        zone.save()
        cust = Customer(zone=zone, name="ACME CHemicals", currency=1, product_range=5, code="A001")
        cust.save()
        order = Order(customer=cust, delivery_cost=642)
        order.save()

        p = Product(name="Perfluoro-2-methylpentane", identifier="FLUTEC PP1", alt_names="FLUTEC PP1 HP,FLUTEC TG-PMP")
        p.save()
        spec1 = Spec(sample_log_product=p, name="QCS 12", product_name="FLUTEC TG PMCP")
        spec1.save()
        spec2 = Spec(sample_log_product=p, name="QCS 19", product_name="FLUTEC PP1C")
        spec2.save()
        
        OrderLine(order=order, spec=spec1, cost_per_kg=235, quantity=100).save()
        OrderLine(order=order, spec=spec2, cost_per_kg=185, quantity=20).save()
        
    
    
    def test_order_line_costs(self):
        spec = Spec.objects.get(name="QCS 12")
        ol = OrderLine.objects.filter(spec=spec).first()
        self.assertEqual(ol.cost_total(), '$23.50')
        self.assertEqual(ol.cost_as_s(), '$2.35')
        self.assertEqual(ol.quantity_as_s(), '10.0 kg')
        


    def test_order_costs(self):
        spec = Spec.objects.get(name="QCS 12")
        o = Order.objects.all().first()
        self.assertEqual(o.total_cost(), 2720)     # = 2350 + 370
        self.assertEqual(o.cost_sub(), '$27.20')
        self.assertEqual(o.cost_delivery(), '$6.42')
        self.assertEqual(o.cost_total(), '$33.62')
        
        
    

    def test_product_name(self):
        spec = Spec.objects.get(name="QCS 12")
        ol = OrderLine.objects.filter(spec=spec).first()
        self.assertEqual(ol.product_name(), 'FLUTEC TG PMCP (QCS 12)')
