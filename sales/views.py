from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from django.contrib.auth.decorators import permission_required
from django.contrib import messages

from .models import *
from samples.models import *
from .pdf_views import *
from util.util import *


LINE_COUNT = 6


def index(request):
    return redirect('/sales/order/')




# Consider calling them territories

def zone_list(request):
    lst = Zone.objects.all().order_by('id')
    context = {
        "lst": lst,
        "obj":Zone,
        "meta_data":Zone.FIELD_LIST,
        'links':{'klass':Zone, 'lst':[]},
        'row_links':['Show', 'Create customer'],
        'title': 'Listing Zones (' + str(len(lst)) + ')',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_list.html", context)
    

def zone_detail(request, obj_id):
    obj = get_object_or_404(Zone, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":Zone.FIELD_LIST,
        'links':{'klass':Zone, 'obj':obj, 'lst':['List', 'Create customer']},
        'title': 'Zone',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_detail.html", context)

"""
# Not user editable - alter through admin console

@permission_required("sales.add_zone")
def zone_create(request):
    obj = Zone()
    context = {
        "obj": obj,
        "meta_data":Zone.FIELD_LIST,
        'links':{'klass':Zone, 'obj':obj, 'lst':['List']},
        'title': 'Creating New Zone',
        'destination':'zone_created',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_create.html", context)

@permission_required("sales.add_zone")
def zone_created(request):
    obj = Zone()
    update(request, obj, Zone.FIELD_LIST)
    return redirect('/sales/zone/' + str(obj.id))


@permission_required("sales.change_zone")
def zone_edit(request, obj_id):
    obj = get_object_or_404(Zone, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":Zone.FIELD_LIST,
        'links':{'klass':Zone, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'Zone',
        'destination':'zone_edited',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_edit.html", context)

@permission_required("sales.change_zone")
def zone_edited(request, obj_id):
    obj = get_object_or_404(Zone, pk=obj_id)
    update(request, obj, Zone.FIELD_LIST)
    return redirect('/sales/zone/' + str(obj.id))
"""

@permission_required("sales.add_customer")
def zone_create_customer(request, obj_id):
    obj = get_object_or_404(Zone, pk=obj_id)
    customer = Customer.create(obj)
    context = {
        "obj": customer,
        "meta_data":Customer.FIELD_LIST,
        'links':{'klass':Customer, 'obj':obj, 'lst':['List']},
        'title': 'Creating New Customer',
        'destination':'customer_created',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_create.html", context)










def customer_list(request):
    lst = Customer.objects.all().order_by('id')
    context = {
        "lst": lst,
        "obj":Customer,
        "meta_data":Customer.FIELD_LIST,
        'links':{'klass':Customer, 'lst':['Create']},
        'row_links':['Show', 'Edit'],
        'title': 'Listing Customers (' + str(len(lst)) + ')',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_list.html", context)
    

def customer_detail(request, obj_id):
    obj = get_object_or_404(Customer, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":Customer.FIELD_LIST,
        'links':{'klass':Customer, 'obj':obj, 'lst':['List', 'Edit', 'Create order', 'Assign specs']},
        'title': 'Customer',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_detail.html", context)

@permission_required("sales.add_customer")
def customer_create(request):
    obj = Customer()
    context = {
        "obj": obj,
        "meta_data":Customer.FIELD_LIST,
        'links':{'klass':Customer, 'obj':obj, 'lst':['List']},
        'title': 'Creating New Customer',
        'destination':'customer_created',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_create.html", context)

@permission_required("sales.add_customer")
def customer_created(request):
    obj = Customer()
    update(request, obj, Customer.FIELD_LIST)
    obj.assign_some_specs()
    return redirect('/sales/customer/' + str(obj.id))


@permission_required("sales.change_customer")
def customer_edit(request, obj_id):
    obj = get_object_or_404(Customer, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":Customer.FIELD_LIST,
        'links':{'klass':Customer, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'Customer',
        'destination':'customer_edited',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_edit.html", context)

@permission_required("sales.change_customer")
def customer_edited(request, obj_id):
    obj = get_object_or_404(Customer, pk=obj_id)
    update(request, obj, Customer.FIELD_LIST)
    return redirect('/sales/customer/' + str(obj.id))

@permission_required("sales.add_order")
def customer_create_order(request, obj_id):
    obj = get_object_or_404(Customer, pk=obj_id)
    order = Order.create(obj)
    #l = OrderLine(order=order)
    lines = [OrderLine(order=order, quantity=0, cost_per_kg=0)] * LINE_COUNT
    specs = obj.specs.all()
    context = {
        "obj": order,
        "meta_data":Order.FIELD_LIST,
        'links':{'klass':Order, 'obj':order, 'lst':['List']},
        'title': f'Creating New Order for {obj.name} (costs are in {obj.currency_name()})',
        'destination':'order_created',
        'subsections':'sales/subsections.html',
        'add_after':'sales/lines_form.html',
        'lines':lines,
        'line_count': len(lines),
        'specs':specs,
    }
    return render(request, "obj_create.html", context)




@permission_required("sales.change_customer")
def customer_assign_specs(request, obj_id):
    obj = get_object_or_404(Customer, pk=obj_id)
    specs = Spec.objects.all()
    print(type(specs.first()))
    context = {
        "obj": obj,
        'links':{'klass':Customer, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'Customer Specifications for ' + obj.name,
        'destination':'customer_assigned_specs',
        'subsections':'sales/subsections.html',
        'tg_specs':Spec.tg_specs(),
        'pp_specs':Spec.pp_specs(),
        'cn_specs':Spec.cn_specs(),
        'other_specs':Spec.other_specs(),
    }
    return render(request, "sales/customer_specs.html", context)


@permission_required("sales.change_customer")
def customer_assigned_specs(request):
    obj = Customer.objects.get(pk=request.POST['id'])
    #print(request.POST)
    obj.specs.all().delete()
    for spec in Spec.objects.all():
        #print(spec.id)
        if f'spec{spec.id}' in request.POST:
            #print('****' + str(spec.id))
            obj.specs.add(spec)
    return redirect('/sales/customer/' + str(obj.id))








def order_list(request):
    lst = Order.objects.all().order_by('id')
    context = {
        "lst": lst,
        "obj":Order,
        "meta_data":Order.FIELD_LIST,
        'row_links':['Show', 'Edit'],
        'title': 'Listing Orders (' + str(len(lst)) + ')',
        'subsections':'sales/subsections.html',
    }
    return render(request, "obj_list.html", context)
    

def order_detail(request, obj_id):
    obj = get_object_or_404(Order, pk=obj_id)
    lines = obj.orderline_set.all()
    links = ['List', 'Edit', 'PDF']
    if obj.status == Order.Status.ORDER_PLACED.value:
        links.append('Finalise')
    
    context = {
        "obj": obj,
        "meta_data":Order.FIELD_LIST,
        'links':{'klass':Order, 'obj':obj, 'lst':links},
        'title': f'Creating New Order for {obj.customer.name} (costs are in {obj.customer.currency_name()})',
        'subsections':'sales/subsections.html',
        'add_after':'sales/lines_list.html',
        'lines':lines,
    }
    return render(request, "obj_detail.html", context)
    
def order_pdf(request, obj_id):
    obj = get_object_or_404(Order, pk=obj_id)
    return create_pdf(obj, 'F2 Customers Export Order')




# Should never be used, but the generic views expect it to exist  
@permission_required("sales.add_order")
def order_create(request):
    obj = Order()
    context = {
        "obj": obj,
        "meta_data":Order.FIELD_LIST,
        'links':{'klass':Order, 'obj':obj, 'lst':['ist', 'Detail']},
        'title': 'Creating New Order for Customer',
        'subsections':'sales/subsections.html',
    }
    return render(request, "sales/order_create.html", context)



@permission_required("sales.add_order")
def order_created(request):
    print(request.POST)
    customer = Customer.objects.get(id=request.POST['customer_id'])
    obj = Order(customer=customer)
    return _order_update(request, obj)

"""

    update(request, obj, Order.FIELD_LIST)
    print(obj.customer)
    print(obj.customer.name)
    print(obj.our_ref)
    print(obj)
    
    line_count = int(request.POST['line_count'])
    print(line_count)
    for i in range(line_count):
        if float(request.POST['quantity_' + str(i)]) == 0:
            continue
        line = OrderLine(order=obj)
        line.spec_id = int(request.POST['product_' + str(i)])
        line.batch = request.POST['batch_' + str(i)]
        line.quantity = float(request.POST['quantity_' + str(i)]) * 10
        line.cost_per_kg = float(request.POST['cost_per_kg_' + str(i)]) * 100
        print(line)
        print(line.spec_id)
        line.save()
        print(line)
    
    # handle lines
    return redirect('/sales/order/' + str(obj.id))
"""    


@permission_required("sales.add_order")
def order_edit(request, obj_id):
    obj = get_object_or_404(Order, pk=obj_id)

    lines = list(obj.orderline_set.all())
    lines.append(OrderLine(order=obj, quantity=0, cost_per_kg=0))
    specs = obj.customer.specs.all()
    context = {
        'title': 'Editing New Order for ' + obj.customer.name,
        'subsections':'sales/subsections.html',
        "obj": obj,
        "meta_data":Order.FIELD_LIST,
        'links':{'klass':Order, 'obj':obj, 'lst':['List', 'Detail']},
        'title': f'Updating Order for {obj.customer.name} (costs are in {obj.customer.currency_name()})',
        'destination':'order_edited',
        'subsections':'sales/subsections.html',
        'add_after':'sales/lines_form.html',
        'lines':lines,
        'line_count': len(lines),
        'specs':specs,
    }
    return render(request, "obj_edit.html", context)



@permission_required("sales.add_order")
def order_edited(request, obj_id):
    obj = get_object_or_404(Order, pk=obj_id)
    return _order_update(request, obj)



def _order_update(request, obj):
    update(request, obj, Order.FIELD_LIST)
    if obj.customer_ref and obj.status == Order.Status.QUOTE.value:
        print('gfd')
        obj.status = Order.Status.ORDER_PLACED.value
    obj.save()

    lines = list(obj.orderline_set.all())  # Convert to a list so it is set in stone

    line_count = int(request.POST['line_count'])
    for i in range(line_count):
        if float(request.POST['quantity_' + str(i)]) == 0:
            continue
        line = OrderLine(order=obj)
        line.spec_id = int(request.POST['product_' + str(i)])
        line.batch = request.POST['batch_' + str(i)]
        line.quantity = float(request.POST['quantity_' + str(i)]) * 10
        line.cost_per_kg = float(request.POST['cost_per_kg_' + str(i)]) * 100
        line.save()

    # Hopefully got the new ones so now safe to delete the old
    for line in lines:
        line.delete()

    return redirect('/sales/order/' + str(obj.id))
    
    
# Need to add further restrictions...!!!
@permission_required("sales.pack_order")
def order_edit_packaging(request, obj_id):
    obj = get_object_or_404(Order, pk=obj_id)

    lines = obj.orderline_set.all()
    context = {
        'title': 'Editing New Order for ' + obj.customer.name,
        'subsections':'sales/subsections.html',
        "obj": obj,
        "meta_data":Order.FIELD_LIST,
        'links':{'klass':Order, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'Creating New Order for ' + obj.customer.name,
        'destination':'order_edited',
        'subsections':'sales/subsections.html',
        'add_after':'sales/lines_links.html' if obj.status == 'ST' else 'sales/lines_list.html',
        'lines':lines,
    }
    return render(request, "obj_edit.html", context)

@permission_required("sales.pack_order")
def order_edited_packaging(request):
    obj = Order()
    update(request, obj, Order.FIELD_LIST)
    return redirect('/sales/order/' + str(obj.id))
    
    
@permission_required("sales.add_order")
def order_finalise(request, obj_id):
    return _order_event('finalise', request, obj_id)
    
@permission_required("sales.pack_order")
def order_start_packing(request, obj_id):
    return _order_event('start_packing', request, obj_id)

@permission_required("sales.pack_order")
def order_packing_done(request, obj_id):
    return _order_event('packing_done', request, obj_id)


def _order_event(event_name, request, obj_id):
    obj = get_object_or_404(Order, pk=obj_id)
    n = obj.event(event_name, request.user)
    messages.info(request, f'Sent {n} e-mail(s).')
    return redirect('/sales/order/' + str(obj.id))
