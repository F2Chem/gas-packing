
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max, Case, When, Value, IntegerField
from django.contrib.auth.decorators import permission_required
from django.utils.timezone import now
from django.core.mail import send_mail
import secret
from .forms import FillingForm, CylinderForm, OrderForm, OrderLineForm
from .models import Filling, Cylinder, Order, Batch

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def home(request):
    return render(request, 'gas_filling/index.html')



def gas_filling(request, pk):
    order = Order.objects.get(pk=pk)

    if request.method == 'POST':
        cylinder_barcode = request.POST.get('cylinder_id')
        if cylinder_barcode:
            filling = Filling.objects.create(
                cylinder=cylinder_barcode,
                order=order,
            )
            return redirect('gas_filling:gas_filling_batchnum', pk=filling.id)

    filling_number = order.fillings.count() + 1

    context = {
        'order': order,
        'filling_number': filling_number,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling.html', context)


def gas_filling_batchnum(request, pk):
    filling = Filling.objects.get(pk=pk)

    last_filling = Filling.objects.exclude(batch_num__isnull=True).order_by('-id').first()
    last_batch_num = last_filling.batch_num if last_filling else None

    if request.method == 'POST':
        batch_num = int(request.POST.get('batch_num'))
        filling.batch_num = batch_num
        filling.save()

        is_new_batch = (last_batch_num is None) or (batch_num != last_batch_num)

        if is_new_batch:
            return redirect('gas_filling:gas_filling_newbatch', pk=filling.id, prev_batch=last_batch_num)

        return redirect('gas_filling:gas_filling_tareweight', pk=filling.id)

    context = {
        'filling': filling,
        'last_batch_num' : last_batch_num,   
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_batch.html', context)


def gas_filling_tareweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        tare_weight = request.POST.get('tare_weight')
        if tare_weight:
            filling.tare_weight = tare_weight
            filling.tare_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_connectionweight', pk=filling.id)
            
    context = {
        'filling': filling, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_tare.html', context)

def gas_filling_connectionweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        connection_weight = request.POST.get('connection_weight')
        if connection_weight:
            filling.connection_weight = connection_weight
            filling.connection_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
    context = {
        'filling': filling, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_connections.html', context)

def gas_filling_endweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        if end_weight:
            filling.end_weight = end_weight
            filling.end_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_pulledweight', pk=filling.id)
    context = {
        'filling': filling, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_end.html', context)

def gas_filling_pulledweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        pulled_weight = request.POST.get('pulled_weight')
        if pulled_weight:
            filling.pulled_weight = pulled_weight
            filling.pulled_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_filling', pk=filling.order.id)
    context = {
        'filling': filling, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_pulled.html', context)

def gas_filling_table(request):
    all_fillings = Filling.objects.all().order_by('-end_time')
    context = {
        'all_filling': all_filling, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_table.html', context)

def gas_filling_home(request):
    context = {
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/home.html', context)

def cylinder_list(request):
    cylinders = Cylinder.objects.all().order_by('id')
    context = {
        'cylinders': cylinders, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/list.html', context)

def cylinder_show(request, pk):
    cylinder = Cylinder.objects.get(pk=pk)
    context = {
        'cylinder': cylinder, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/show.html', context)

def cylinder_edit(request, pk):
    cylinder = Cylinder.objects.get(pk=pk)
    if request.method == 'POST':
        form = CylinderForm(request.POST, instance=cylinder)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:cylinder_list')
    else:
        form = CylinderForm(instance=cylinder)

    context = {
        'form': form, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/edit.html', context)

def cylinder_create(request):
    if request.method == 'POST':
        form = CylinderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:gas_filling_home')
    else:
        form = CylinderForm()

    context = {
        'form': form, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/create.html', context)

def order_list(request):
    orders = Order.objects.annotate(
        status_order=Case(
            When(status='OPEN', then=Value(0)),
            When(status='IN_PROGRESS', then=Value(1)),
            When(status='PACKED', then=Value(2)),
            When(status='PASSED', then=Value(3)),
            When(status='FAILED', then=Value(4)),
            When(status='REWORKED', then=Value(5)),
            When(status='FINISHED', then=Value(6)),
            output_field=IntegerField()
        )
    ).order_by('status_order', 'id')
    
    for order in orders:
        if order.status == 'OPEN' and order.fillings.exists():
            order.status = 'IN_PROGRESS'
            order.save()

    context = {
        'orders': orders, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/order_list.html', context)


def order_create(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        orderline_form = OrderLineForm(request.POST)
        if order_form.is_valid() and orderline_form.is_valid():
            order = order_form.save()
            orderline = orderline_form.save(commit=False)
            orderline.order = order
            orderline.save()

            send_mail(
                f'Order #{order.id} has been created.',
                f'Customer: {order.customer}. Comments: {order.packaging_instruction}.',
                secret.FROM_EMAIL,
                [secret.TO_EMAIL],
            )

            return redirect('gas_filling:order_list')
    else:
        order_form = OrderForm()
        orderline_form = OrderLineForm()

    context = {
        'form': order_form, 
        'orderline_form': orderline_form,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/order_create.html', context)


def order_show(request, pk):
    order = Order.objects.get(pk=pk)

    if order.status == 'OUTSTANDING' and order.fillings.exists():
        order.status = 'IN_PROCESS'
        order.save()

    fillings = order.fillings.all().order_by('id')
    context = {
        'order': order,
        'fillings': fillings,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/order_show.html', context)



def order_edit(request, pk):
    order = Order.objects.get(pk=pk)
    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            order_form.save()
            return redirect('gas_filling:order_list')
    else:
        order_form = OrderForm(instance=order)

    context = {
        'order': order,
        'form': order_form,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/order_edit.html', context)


def filling_show(request, pk):
    filling = get_object_or_404(Filling, pk=pk)
    context = {
        'filling': filling,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_show.html', context)

def filling_edit(request, pk):
    filling = Filling.objects.get(pk=pk)
    if request.method == 'POST':
        form = FillingForm(request.POST, instance=filling)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:filling_show', pk=filling.id)
    else:
        form = FillingForm(instance=filling)

    context = {
        'filling': filling,
        'form': form,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_edit.html', context)

def continue_filling(request, pk):
    filling = Filling.objects.get(pk=pk)

    if not filling.batch_num:
        return redirect('gas_filling:gas_filling_batchnum', pk=filling.id)
    elif not filling.tare_weight:
        return redirect('gas_filling:gas_filling_tareweight', pk=filling.id)
    elif not filling.end_weight:
        return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
    else:
        return redirect('gas_filling:gas_filling', pk=filling.order.id)

def order_status(request, pk):
    order = Order.objects.get(pk=pk)    

    if request.method == 'POST':
        if order.status == 'IN_PROGRESS':
            order.status = 'PACKED'
            send_mail(
                f'Order Finished',
                f'Order #{order.id} has been completed.',
                secret.FROM_EMAIL,
                [secret.TO_EMAIL],
            )
        elif order.status == 'PACKED':
            order.status = 'PASSED'
            send_mail(
                f'Order Released',
                f'Order #{order.id} has been released.',
                secret.FROM_EMAIL,
                [secret.TO_EMAIL],
            )
        order.save()        

        return redirect('gas_filling:order_list')

    context = {
        'order': order,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/order_status.html', context)


def order_test(request):
    print('In order_test')
    raise Exception("Error!")


def orderline_create(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderLineForm(request.POST)
        if form.is_valid():
            orderline = form.save(commit=False)
            orderline.order = order
            orderline.save()
            return redirect('gas_filling:order_show', order_id)
    else:
        form = OrderLineForm()

    return render(request, 'gas_filling/orderline_create.html', {'form': form, 'order': order})


def new_batch(request, pk, prev_batch):
    filling = get_object_or_404(Filling, pk=pk)
    order = filling.order
    current_batch_num = filling.batch_num
    prev_batch = prev_batch

    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        start_weight = request.POST.get('start_weight')

        if prev_batch:
            Batch.objects.update_or_create(
                batch_num=prev_batch,
                parent_order=order,
                defaults={'end_weight': end_weight}
            )

        Batch.objects.update_or_create(
            batch_num=current_batch_num,
            parent_order=order,
            defaults={'start_weight': start_weight}
        )

        return redirect('gas_filling:gas_filling_tareweight', pk=filling.id)

    context = {
        'filling': filling,
        'batch_num': current_batch_num,
        'order': order,
        'prev_batch': prev_batch,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/new_batch.html', context)

def batch_list(request):
    batches = Batch.objects.all().order_by('-id')
    context = {
        'batches': batches,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/batch_list.html', context)

def pdf_create(request):
    document = []

    document.append(Spacer(1, 20))
    document.append(Paragraph('Summary of Orders and Batches', ParagraphStyle(name='Aloy', fontfamily="Helvetica", fontSize=16, alignment=TA_CENTER)))
    document.append(Spacer(1, 30))

    def organiseOrder(order):
        text = ""
        text += "Customer: " + order.customer
        if order.comments:
            text += ", Comments: " + order.comments
        text += ", Created Time: " + str(order.created_time)
        text += ", Total Fills: " + str(order.total_fills)
        text += ", Total Weight of Fills: " + str(order.total_fill_weight)
        text += ", Order Status: " + order.status
        return text
    
    def organiseFilling(filling):
        text = ""
        text += "Cylinder: " + filling.cylinder
        text += ", Cylinder Time: " + str(filling.cylinder_time)
        text += ", Batch Number: " + str(filling.batch_num)
        text += ", Tare Weight: " + str(filling.tare_weight)
        text += ", " + str(filling.tare_time)
        text += ", Heel Weight: " + str(filling.heel_weight)
        text += ", Connection Weight: " + str(filling.connection_weight)
        text += ", " + str(filling.connection_time)
        text += ", End Weight: " + str(filling.end_weight)
        text += ", " + str(filling.end_time)
        text += ", Pulled Weight: " + str(filling.pulled_weight)
        text += ", " + str(filling.pulled_time)
        text += ", Filling Weight: " + str(filling.fill_weight)
        return text


    def organiseBatch(batch):
        text = ""
        text += "Batch Number: " + batch.batch_num
        text += ", Start Weight: " + batch.start_weight
        text += ", End Weight: " + batch.end_weight
        return text

    for order in Order.objects.all():
        document.append(Paragraph(organiseOrder(order), ParagraphStyle(name='Lara', fontfamily="Helvetica", fontSize=8, alignment=TA_JUSTIFY)))
        for filling in order.fillings.all():
            document.append(Spacer(1,2))
            document.append(Paragraph(organiseFilling(filling), ParagraphStyle(name='Kyle', fontfamily="Helvetica", fontSize=6, alignment=TA_JUSTIFY, leftIndent=20)))
        document.append(Spacer(1,5))

    SimpleDocTemplate('OrdersBatches.pdf', pagesize=A4, rightMargin=12, leftMargin=12, topMargin=12, bottomMargin=6).build(document)

    context = {
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/pdf_create.html', context)