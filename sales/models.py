import re
import datetime

from django.db import models
from django.utils.html import mark_safe
from django.core.mail import send_mail


from util.util import month_and_year, TimeStampMixin, create_url
from samples.models import Product, Spec#, Sample



"""
It is envisaged that zones will  be set up by admin, and uses can then add customers to a zone.
Once a customer is in the system, orders and and quotes can be created for them.

An order goes through a number of steps, and its progress is tracked with "status".



"""






"""
A Zone is an area of the world; all companies in a zone have the same regulations.
A zone can only be edits and created via the admin interface, but you can list them and view them - customers are created from a zone
"""
class Zone(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    delivery_terms = models.CharField(max_length=255, blank=True, null=True)
    export_statement = models.TextField(blank=True, null=True)
    tariff = models.TextField(blank=True, null=True)  # !!! or is the PFC dependant???
    comments = models.TextField(blank=True, null=True)
    currency = models.IntegerField(default=0)

    CURRENCIES = [
        {'name':"Sterling", 'symbol':"£"},
        {'name':"US dollars", 'symbol':"$"},
        {'name':"Euros", 'symbol':"€"},
    ]

    class Meta:
        managed = True
        db_table = 'sales_zones'

    URL_NAME = 'zone'
    FIELD_LIST = [
        {'heading': "Name", 'column': 'name'},
        {"heading": "Currency", "column": "currency", "options_from_array":CURRENCIES},
        {'heading': "Delivery terms", 'column': 'delivery_terms', 'no_list':True},
        {'heading': "Customs tariff number", 'column': 'tariff', 'no_list':True},
        {'heading': "Export statement", 'column': 'export_statement', 'no_list':True},
        {'heading': "Comments", 'column': 'comments', 'no_list':True},
    ]
    
    def __str__(self):
        return 'Zone: ' + self.name








"""
A Customer is a destination. If a company has several sites, each should be a different Cusomer object.
Customers belong to a Zone.

Do we want an address record? Or have address (invoice AND delivery) in the customer?
"""
class Customer(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=8, blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    invoice_address = models.TextField(blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    packing_note = models.TextField(blank=True, null=True)
    currency = models.IntegerField(default=0)
    product_range = models.IntegerField(default=0) # Determines the initial set of specs, but also how the products are named

    #default_spec = models.ForeignKey(Spec, on_delete=models.CASCADE, blank=True, null=True)

    specs = models.ManyToManyField(Spec)



    # The symbol is used to determine which name to use
    # This means it can only be CN, PP, PC, HP or TG, as these are the only fields for perfluorocarbons
    # What of non-perfluorocarbons?   !!!
    PRODUCT_RANGES = [
        {'name':"Chemical", 'symbol':"CN"},
        {'name':"Electronics", 'symbol':"PP"},
        {'name':"Cosmetics", 'symbol':"PC"},
        {'name':"High purity", 'symbol':"HP"},
        {'name':"Tracer grade", 'symbol':"TG"},
        #{'name':"Dimer/trimer", 'symbol':"DT"},
        #{'name':"Foam blowing", 'symbol':"RC"},
    ]



    class Meta:
        managed = True
        db_table = 'sales_customers'

    URL_NAME = 'customer'
    FIELD_LIST = [
        {'heading': "Name", 'column': 'name'},
        {'heading': "Code", 'column': 'code'},
        {'heading': "Zone", 'column': 'zone_id', 'options_from_table': 'sales.models.Zone', 'attribute': 'name', 'no_list':True},
        {"heading": "Currency", "column": "currency", "options_from_array":Zone.CURRENCIES, 'no_list':True},
        {"heading": "Product range", "column": "product_range", "options_from_array":PRODUCT_RANGES, 'no_list':True},
        {'heading': "Invoice address", 'column': 'invoice_address', 'no_list':True},
        {'heading': "Delivery address", 'column': 'delivery_address', 'copy_from':'invoice_address', 'no_list':True},
        {'heading': "Delivery address", 'func':lambda o:o.delivery_address if o.delivery_address else o.invoice_address, 'list_only':True},
        {'heading': "Packing note template", 'column': 'packing_note', 'no_list':True},
        {'heading': "Comments", 'column': 'comments', 'no_list':True},
        {'heading': "Relevant specifications", 'func':lambda o:o.list_specs_as_s(), 'no_list':True, 'no_edit':True},
    ]
    
    def __str__(self):
        return 'Customer: ' + self.name

    # Used in zone_create_customer
    # Unit tested
    def create(zone):
        customer = Customer(zone_id=zone.id, currency=zone.currency)
        return customer



    # Called after the customer has been created in the view
    # Unit tested
    def assign_some_specs(self):
        match Customer.PRODUCT_RANGES[self.product_range]['name']:
            case 'Any':
                self._assign_some_specs(Spec.objects.all())
            case 'Chemical':
                self._assign_some_specs(Spec.objects.filter(product_name__startswith="Perfluoro").order_by('product_name') | Spec.objects.filter(name__startswith="Octafluoro"))
            case 'Electronics':
                self._assign_some_specs(Spec.objects.filter(product_name__startswith="FLUTEC PP").order_by('product_name'))
            case 'Cosmetics':
                self._assign_some_specs(Spec.objects.filter(product_name__startswith="FLUTEC PC").order_by('product_name'))
            case 'High purity':
                self._assign_some_specs(Spec.objects.filter(product_name__startswith="FLUTEC HP").order_by('product_name'))
            case 'Tracer grade':
                self._assign_some_specs(Spec.objects.filter(product_name__startswith="FLUTEC TG").order_by('product_name'))
            #case 'Foam blowing':
            #    self._assign_some_specs(Spec.objects.filter(product_name__startswith="FLUTEC RC").order_by('product_name')
            #case 'Dimer/trimer':
            #    return Spec.objects.filter(product_name__startswith="HFP ")


    # Internal, used by above only, no need to unit test
    def _assign_some_specs(self, specs):
        for spec in specs:
            self.specs.add(spec)


    # Djano will ensure no duplicates
    # Unit tested
    def add_spec(self, spec):
        self.specs.add(spec)

    # Djano will ensure no duplicates
    # Unit tested
    def remove_spec(self, spec):
        self.specs.remove(spec)


    # Unit tested
    def list_specs_as_s(self):
        specs = self.specs.all()
        if len(specs) == 0:
            return '---None set---'
        
        lst = list(map(lambda el: el.__str__(), specs))
        return ', '.join(lst)





    # Unit tested
    def currency_name(self):
        return Zone.CURRENCIES[self.currency]['name']


    # Assumes x is in pennies or cents
    # Returns a dash if no value or the value is zero.
    # Not designed to handle negative numbers
    # Unit tested
    def show_money(self, x):
        if not x:
            return '-'
        symbol = Zone.CURRENCIES[self.currency]['symbol']
        number = "%.2f" % (x / 100.0)
        return f'{symbol}{number}'        


    # Unit tested
    def product_name(self, pfc):
        if Customer.PRODUCT_RANGES[self.product_range]['symbol'] == 'CN':
            return pfc.name
        return getattr(pfc, Customer.PRODUCT_RANGES[self.product_range]['symbol'].lower() + '_value')


    # Unit tested
    def find_product_range_index(s):
        if type(s) == int:
            return s
        s = s.lower()
        for i, el in enumerate(Customer.PRODUCT_RANGES):
            if s == el['name'].lower() or s == el['symbol'].lower():
                return i
        return None
        
        
   
        

    # Just for testing - not unit tested
    def kick_start():
        zone_data = [
            {'name':'UK', 'currency':0},
            {'name':'EU', 'currency':2},
            {'name':'USA', 'currency':1},
            {'name':'Far east', 'currency':0},
            {'name':'Rest of world', 'currency':1},
            #{'name':'', ;currency:},
        ]
        Zone.objects.all().delete()
        for el in zone_data:
            Zone(name=el['name'], currency=el['currency']).save()

        customer_data = [
            {'name':'British Medicines', 'zone':'UK', 'product_range':4, 'code':'B001'},
            {'name':'Germn Tracer Company', 'zone':'EU', 'product_range':5, 'code':'G001'},
            {'name':'Acme Cooling', 'zone':'USA', 'product_range':2, 'code':'A001'},
            {'name':'University of Shanghai', 'zone':'Far east', 'product_range':1, 'code':'U001'},
        ]
        Customer.objects.all().delete()
        for el in customer_data:
            zone = Zone.objects.get(name=el['zone'])
            Customer(name=el['name'], zone=zone, currency=zone.currency, product_range=el['product_range']).save()




"""
class CustomerSpec(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE)


    class Meta:
        managed = True
        db_table = 'sales_customer_specs'
"""



# An order belongs to a customer, and has multiple OrderLine objects
# An order passes though a number of stages, tracked with status
# May want to skip step one, or steps one and two
class Order(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    our_ref = models.CharField(max_length=32, blank=True, null=True)
    customer_ref = models.CharField(max_length=32, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    delivery_cost = models.IntegerField(blank=True, null=True) # In pennies or cents
    sales_comments = models.TextField(blank=True, null=True)
    packager_comments = models.TextField(blank=True, null=True)
    dispatcher_comments = models.TextField(blank=True, null=True)
    date_placed = models.DateField(blank=True, null=True)
    date_required = models.DateField(blank=True, null=True)
    date_delivered = models.DateField(blank=True, null=True)

    status = models.IntegerField(default=0)
    status_log = models.TextField(default='')

    courier = models.CharField(max_length=32, blank=True, null=True)
    courier_ref = models.CharField(max_length=32, blank=True, null=True)
    
    STATUSES = [
        {
          'symbol':'EQ',
          'name':'Enquiry',
          'msg':'If the customer has decided what theyt want (products and quantities), you can convert an enquiry to a quote.',
        },
        {
          'symbol':'QT',
          'name':'Quote',
          'msg':'Give a quote a customer reference number to make it into a firm order. You will still be able to modify it',
          'permission_to_progess':'sales',
        },
        {
          'symbol':'PL',
          'name':'Order placed',
          'msg':'Click <i>Finalise</i> to complete an order, and send an alert that it is ready to be packed',
          'permission_to_progess':'sales',
        },
        {
          'symbol':'RP',
          'name':'Ready for packing',
          'msg':'Click <i>Start packing</i> to signal you are about to start packing the order',
          'permission_to_progess':'sales',
        },
        {
          'symbol':'ST',
          'name':'Packing started',
          'msg':'Click <i>Packing completed</i> to signal you have finished packing the order',
          'permission_to_progess':'packing',
        },
        {
          'symbol':'CP',
          'name':'Packing completed',
          'msg':'Click <i>collected</i> to signal the order has been collected',
          'permission_to_progess':'packing',
        },
        {
          'symbol':'CL',
          'name':'Collected',
          'msg':'Click <i>Delivered</i> to signal the order has been delivered',
          'permission_to_progess':'sales',
        },
        {
          'symbol':'DL',
          'name':'Delivered',
        },
        {
          'symbol':'C1',
          'name':'Cancelled prior to despatch',
        },
        {
          'symbol':'C2',
          'name':'Cancelled after despatch',
        },
        {
          'symbol':'C3',
          'name':'Cancelled after despatch, goods returned',
        },
    ]
    


    class Meta:
        managed = True
        db_table = 'sales_orders'


    URL_NAME = 'order'
    FIELD_LIST = [
        #{'heading': "Customer", 'column': 'customer_id', 'options_from_table': 'sales.models.Customer', 'attribute': 'name', 'read_only':True},
        {'heading': "Status", 'func':lambda o:o.status_name()},
        {'heading': "Our reference", 'column': 'our_ref'},
        {'heading': "Customer reference", 'column': 'customer_ref'},
        {'heading': "Date required", 'column': 'date_required'},
        {'heading': "Delivery cost", 'column': 'delivery_cost', 'money':True},
        {'heading': "Sales notes", 'column': 'sales_comments'},
        {'heading': "Packer's notes", 'column': 'packager_comments', 'read_only':True},
    ]
    
    # These fields for the packer
    ALT_FIELD_LIST = [
        #{'heading': "Customer", 'column': 'customer_id', 'options_from_table': 'sales.models.Customer', 'attribute': 'name', 'read_only':True},
        {'heading': "Status", 'column': 'status', 'read_only':True},
        {'heading': "Our reference", 'column': 'our_ref', 'read_only':True},
        {'heading': "Customer reference", 'column': 'customer_ref', 'read_only':True},
        {'heading': "Date required", 'column': 'date_required', 'read_only':True},
        {'heading': "Delivery cost", 'column': 'delivery_cost', 'money':True, 'read_only':True},
        {'heading': "Sales notes", 'column': 'sales_comments', 'read_only':True},
        {'heading': "Packer's notes", 'column': 'packager_comments'},
    ]
    
    def __str__(self):
        return f'Order: {self.customer.name} ({self.our_ref})'


    # Unit tested
    def create(customer):
        order = Order(customer_id=customer.id)
        order.packing_note = customer.packing_note
        if customer.code:
            last = Order.objects.filter(customer=customer).last()
            if last and last.our_ref:
                md = re.search(r'\/(\d+)', last.our_ref)
                mx = int(md.group(1))
                order.our_ref = customer.code + '/' + str(mx + 1)
            else:
                order.our_ref = customer.code + '/1'
        return order





    # Four methods for handling status
    # All unit tested in test_status_various
    def set_status(self, name):
        if type(name) == int:
            self.status = name
        else:
            i, el = Order.get_status_with_index(name)
            if el:
                self.status = i
            else:
                raise Exception(f'Status not found for Slaves/Order: {name}')

    def status_name(self):
        return Order.STATUSES[self.status]['name']

    def status_msg(self):
        return Order.STATUSES[self.status]['msg']
        
    def get_status_with_index(s):
        for i, el in enumerate(Order.STATUSES):
            if el['symbol'] == s or el['name'] == s:
                return i, el
        return -1, None



    # Call this method to signal the order has moved to a new status.
    # The status is updated. The user is noted as well as the date.
    # TODO email packager
    # The order is saved.
    def event(self, event_name, user):
        self.status, status = Order.get_status_with_index(event_name)
        status_name = status['name']
        self.status_log += f'\n{datetime.date.today()} {status_name} by {user.username}'
        self.save()
        
        url = create_url('sales/order/' + str(self.id))
        return self.send_alert(status_name, f'Order for {self.customer.name}: {status_name}. Click <a href="{url}">here</a> for more details.')

    def send_alert(self, event_name, event_msg):
        lst = []
        for email in SalesEmail.objects.all():
            if event_name in email.events:
                lst.append(email.email())
        result = send_mail(          # result is 1 or 0
            "Alert from F2DB/Sales",
            '',
            "f2db@f2chemicals.com",
            lst,
            fail_silently=False,
            html_message=event_msg
        )
        return len(lst) * result
        













   # These four mthods are unit tested in OrderLineTests.test_order_costs
   # Gets the total cost of this order, excluding delivery as an integer, in pennies of cents
    def total_cost(self):
        total = 0
        for line in self.orderline_set.all():
            total += line.quantity * line.cost_per_kg
        return total / 10
    # Gets the total cost of this order, excluding delivery, as a string
    def cost_sub(self):
        return self.customer.show_money(self.total_cost())
    # Gets the deluvery cost of this order as a string
    def cost_delivery(self):
        return self.customer.show_money(self.delivery_cost) if self.delivery_cost else 'TBC'
    # Gets the total cost of this order, including delivery, as a string
    def cost_total(self):
        dc = self.delivery_cost if self.delivery_cost else 0
        return self.customer.show_money(self.total_cost() + dc)



"""
A OrderLine is a part of a order - one line per product.
Should be created/edited on the same page as its Order.
Can quantity or cost ever be non-integers?
"""
class OrderLine(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    spec = models.ForeignKey(Spec, on_delete=models.CASCADE)
    #sample = models.ForeignKey(Sample, on_delete=models.CASCADE, blank=True, null=True)   # link to batch
    is_delivery = models.BooleanField(default=False)
    is_volume = models.BooleanField(default=False)
    quantity = models.IntegerField(blank=True, null=True) # In 0.1 kg parts (so divide by 10 to get amount in kg)
    cost_per_kg = models.IntegerField(blank=True, null=True) # In pennies or cents
    packing_note = models.TextField(blank=True, null=True)
    date_packed = models.DateField(blank=True, null=True)
    packed_by = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sales_lines'




    def quantity_div(self):
        return self.quantity / 10.0

    def cost_per_kg_div(self):
        return self.cost_per_kg / 100.0

    
    
    
   # These four mthods are unit tested in OrderLineTests.test_order_line_costs
    def __str__(self):
        return 'Line: ' + str(self.quantity) + ' kg of batch ' + self.batch
    def cost_total(self):
        return self.order.customer.show_money(self.quantity * self.cost_per_kg / 10.0)
    def cost_as_s(self):
        return self.order.customer.show_money(self.cost_per_kg)
    def quantity_as_s(self):
        return f'{"%.1f" % (self.quantity / 10.0)} kg'



    #def set_product(self, product_name):
    #    self.product = Product.search(product_name)
    #    if not self.product:
    #        raise Exception('Failed to find product: ' + product_name)



    # Unit tested
    def product_name(self):
        return self.spec.product_name + ' (' + self.spec.name + ')'





"""
A OrderLine is a part of a order - one line per product.
Should be created/edited on the same page as its Order.
Can quantity or cost ever be non-integers?
"""
class Instruction(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)

    event = models.CharField(max_length=16, blank=True, null=True)
    condition = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'sales_instructions'

   
   
class SalesEmail(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    events = models.TextField(default='')

    class Meta:
        managed = True
        db_table = 'sales_emails'

    def email(self):
        return self.name + '@f2chemicals.com'

    