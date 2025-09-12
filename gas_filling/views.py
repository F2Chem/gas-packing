
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max, Case, When, Value, IntegerField
from django.contrib.auth.decorators import permission_required
from django.utils.timezone import now
from django.core.mail import send_mail
import secret
from .forms import FillingForm, CylinderForm, OrderForm, OrderLineForm
from .models import *
from datetime import date, timedelta


from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def home(request):
    return render(request, 'gas_filling/index.html')


def gas_filling(request, pk):
    order_line = OrderLine.objects.get(pk=pk)
    order = order_line.order

    fill_progress = (str((order_line.cylinders_somewhat_filled()) + 1) + "/" + str(order_line.num_cylinders))

    if request.method == 'POST':
        barcode = request.POST.get('cylinder_id', '').strip()
        if barcode:
            try:
                cylinder = Cylinder.objects.get(barcodeid=barcode)
                cylinder_testdate = cylinder.check_in_date()
                alert_message = None
                if cylinder_testdate == 2:
                    alert_message = "Cylinder has expired!"
                    return render(request, 'gas_filling/filling.html', {
                        'order': order,
                        'order_line': order_line,
                        'filling_number': order_line.fillings.count(),
                        'alert_message': alert_message,
                        'subsections': 'gas_filling/subsections.html',
                    })
                elif cylinder_testdate == 1:
                    alert_message = "Cylinder approaching expiry"
                    return render(request, 'gas_filling/filling.html', {
                        'order': order,
                        'order_line': order_line,
                        'filling_number': order_line.fillings.count(),
                        'alert_message': alert_message,
                        'subsections': 'gas_filling/subsections.html',
                    })
                filling = Filling.objects.create(
                    cylinder=cylinder,
                    order_line=order_line,
                    filling_number = order_line.fillings.count() + 1
                )
                return redirect('gas_filling:gas_filling_batchnum', pk=filling.id)
            except (Cylinder.DoesNotExist, ValueError):
                return redirect('gas_filling:cylinder_create', barcode=barcode, orderline_id=order_line.pk)            

    context = {
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling.html', context)


def gas_filling_batchnum(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))
    last_filling = Filling.objects.exclude(batch_num__isnull=True).order_by('-id').first()
    last_batch_num = last_filling.batch_num if last_filling else 0

    if request.method == 'POST':
        batch_num = int(request.POST.get('batch_num'))
        filling.batch_num = batch_num
        filling.save()

        is_new_batch = (last_batch_num is None) or (batch_num != last_batch_num)

        if is_new_batch:
            return redirect('gas_filling:gas_filling_newbatch', pk=filling.id, prev_batch=last_batch_num)

        return redirect('gas_filling:gas_filling_recyclenum', pk=filling.id)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'last_batch_num': last_batch_num,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_batch.html', context)


def gas_filling_recyclenum(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))
    last_filling = Filling.objects.exclude(recycle_num__isnull=True).order_by('-id').first()
    last_recycle_num = last_filling.recycle_num if last_filling else 0

    if request.method == 'POST':
        recycle_num = int(request.POST.get('recycle_num'))
        filling.recycle_num = recycle_num
        filling.save()

        is_new_recycle = (last_recycle_num is None) or (recycle_num != last_recycle_num)
        if is_new_recycle:
            return redirect('gas_filling:gas_filling_newrecycle', pk=filling.id, prev_recycle=last_recycle_num)

        return redirect('gas_filling:gas_filling_heelweight', pk=filling.id)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'last_recycle_num': last_recycle_num,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_recycle.html', context)


def gas_filling_heelweight(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order
    cylinder = filling.cylinder

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))

    if request.method == 'POST':
        heel_weight = float(request.POST.get('heel_weight'))
        filling.heel_weight = heel_weight
        filling.heel_time = now()

        difference = round(heel_weight - cylinder.tare, 2)

        if filling.order_line.cylinder_type == "STILLAGE":
            filling.heel_weight_b = heel_weight
            filling.save()
            return redirect('gas_filling:gas_filling_heelweight_b', pk=filling.id)

        if difference != 0:
            if order_line.keep_heel:
                filling.save()
                return redirect('gas_filling:gas_filling_connectionweight', pk=filling.id)
            else:
                filling.heel_weight_b = heel_weight
                filling.save()
                return redirect('gas_filling:gas_filling_heelweight_b', pk=filling.id)
        else:
            filling.save()
            return redirect('gas_filling:gas_filling_connectionweight', pk=filling.id)


    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'cylinder': cylinder,
        'fill_progress': fill_progress,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_heel.html', context)

def gas_filling_heelweight_b(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order
    cylinder = filling.cylinder

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))

    if filling.order_line.cylinder_type != "STILLAGE":
        difference = round(filling.heel_weight_b - cylinder.tare, 2)
        error_message = ("A heel of " + str(difference) + "kg was detected. This order line does not allow keeping heels. Remove the heel and weigh again.")
    else:
        error_message = ("Now remove stillage heel and weigh again.")

    if request.method == 'POST':
        heel_weight = float(request.POST.get('heel_weight'))
        if heel_weight != filling.heel_weight_b or order_line.cylinder_type == "STILLAGE":
            filling.heel_weight = heel_weight
            filling.heel_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_connectionweight', pk=filling.id)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'cylinder': cylinder,
        'fill_progress': fill_progress,
        'error_message': error_message,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_heel_b.html', context)


def gas_filling_connectionweight(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))

    if request.method == 'POST':
        connection_weight = request.POST.get('connection_weight')
        if connection_weight:
            filling.connection_weight = connection_weight
            filling.connection_time = now()
            filling.save()
            if order_line.cylinder_type == "STILLAGE":
                Stillage.objects.get_or_create(stillage_num=Stillage.objects.filter(filling=filling).count(), filling = filling)
            return redirect('gas_filling:gas_filling_endweight', pk=filling.id)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_connections.html', context)


def gas_filling_endweight(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order
    cylinder = filling.cylinder
    stillage = None
    if order_line.cylinder_type == "STILLAGE":
        stillage, created = Stillage.objects.get_or_create(stillage_num=Stillage.objects.filter(filling=filling).count()-1, filling = filling)

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))
    stillage_progress = None
    connections = filling.connection_weight - filling.heel_weight
    target_weight = round(cylinder.tare + order_line.fill_weight + connections, 2)
    if stillage:
        stillage_progress = (str(Stillage.objects.filter(filling=filling).count()))
        target_weight = round(filling.heel_weight + order_line.fill_weight + connections, 2)
    

    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        if end_weight:
            if stillage:
                stillage.end_weight = end_weight
                stillage.end_time = now()
                stillage.save()
                if Stillage.objects.filter(filling=filling).count() < order_line.num_cylinders:
                    Stillage.objects.get_or_create(stillage_num=Stillage.objects.filter(filling=filling).count(), filling = filling)
                    return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
                end_weight = stillage.finished_end_weight(filling)
            filling.end_weight = end_weight
            filling.end_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_pulledweight', pk=filling.id)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'stillage_progress': stillage_progress,
        'target_weight': target_weight,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_end.html', context)


def gas_filling_pulledweight(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order
    cylinder = filling.cylinder
    stillage = None
    if order_line.cylinder_type == "STILLAGE":
        stillage = Stillage.objects.filter(filling=filling, pulled_time=None).exclude(end_time=None).order_by("end_time").first()

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))
    stillage_progress = None
    target_weight = round(cylinder.tare + order_line.fill_weight, 2)
    if stillage:
        stillage_progress = (str(order_line.num_cylinders+1-Stillage.objects.filter(filling=filling, pulled_time=None).count()))
        target_weight = round(filling.heel_weight + order_line.fill_weight, 2)
    

    if request.method == 'POST':
        pulled_weight = request.POST.get('pulled_weight')
        if pulled_weight:
            if stillage:
                stillage.pulled_weight = pulled_weight
                stillage.pulled_time = now()
                stillage.save()
                if (order_line.num_cylinders - Stillage.objects.filter(filling=filling, pulled_time=None).count()) < order_line.num_cylinders:
                    return redirect('gas_filling:gas_filling_pulledweight', pk=filling.id)
                pulled_weight = stillage.finished_pulled_weight(filling)
                
            filling.pulled_weight = pulled_weight
            filling.pulled_time = now()
            filling.save()
            
            if order_line.all_somewhat_filled():
                return redirect('gas_filling:order_show', pk=order.id)
            else:
                return redirect('gas_filling:gas_filling_filling', pk=order_line.id)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'stillage_progress': stillage_progress,
        'target_weight': target_weight,
        'subsections': 'gas_filling/subsections.html',
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
    cylinders = Cylinder.objects.all().order_by('test_date')
    
    for cyl in cylinders:
        status_code = cyl.check_in_date()
        cyl.status = status_code
        
        if status_code == 2:
            cyl.status_text = 'Expired'
        elif status_code == 1:
            cyl.status_text = 'Expiring Soon'
        else:
            cyl.status_text = 'Valid'

    context = {
        'cylinders': cylinders, 
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/list.html', context)

def cylinder_show(request, pk):
    cylinder = Cylinder.objects.get(pk=pk)

    status_code = cylinder.check_in_date()
    cylinder.status = status_code
    
    if status_code == 2:
        cylinder.status_text = 'Expired'
    elif status_code == 1:
        cylinder.status_text = 'Expiring Soon'
    else:
        cylinder.status_text = 'Valid'

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

def cylinder_create(request, barcode, orderline_id):
    order_line = get_object_or_404(OrderLine, pk=orderline_id)
    order = order_line.order


    if request.method == 'POST':
        form = CylinderForm(request.POST)
        if form.is_valid():
            cylinder = form.save()
            cylinder_testdate = cylinder.check_in_date()

            alert_message = None
            if cylinder_testdate == 2:
                alert_message = "Cylinder has expired!"
            elif cylinder_testdate == 1:
                alert_message = "Cylinder approaching expiry"

            if alert_message:
                form = CylinderForm()

                context = {
                    'form': form,
                    'barcode': barcode,
                    'orderline_id': orderline_id,
                    'order_line': order_line,
                    'alert_message': alert_message,
                    'subsections': 'gas_filling/subsections.html',
                }
                return render(request, 'gas_filling/create.html', context)
            
            filling = Filling.objects.create(
                cylinder=cylinder,
                order_line=order_line,
            )
            return redirect('gas_filling:gas_filling_batchnum', pk=filling.id)
      
    else:
        form = CylinderForm(initial={'barcodeid': barcode})

    context = {
        'form': form,
        'barcode': barcode,
        'orderline_id': orderline_id,
        'order_line' : order_line,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/create.html', context)

def order_list(request):
    status_filter = request.GET.get("status")

    orders = Order.objects.annotate(
        status_order=Case(
            When(status='OPEN', then=Value(1)),
            When(status='CLOSED', then=Value(2)),
            When(status='IN_PROGRESS', then=Value(3)),
            When(status='PACKED', then=Value(4)),
            When(status='PASSED', then=Value(5)),
            When(status='FAILED', then=Value(6)),
            When(status='REWORKED', then=Value(7)),
            When(status='FINISHED', then=Value(8)),
            default=Value(100),
            output_field=IntegerField()
        )
    ).order_by('-id')

    if status_filter:
        orders = orders.filter(status=status_filter)
    
    for order in orders:
        if order.status == 'OPEN' and order.fillings.exists():
            order.status = 'IN_PROGRESS'
            order.save()
        if order.status == 'CLOSED' and order.fillings.exists():
            order.status = 'IN_PROGRESS'
            order.save()

    context = {
        'orders': orders, 
        'status_filter': status_filter,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/order_list.html', context)


def order_create(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        orderline_form = OrderLineForm(request.POST)

        if order_form.is_valid() and orderline_form.is_valid():
            order = order_form.save(commit=False)
            orderline = orderline_form.save(commit=False)
            orderline.order = order
            orderline.line_number = 1

            order.save()
            orderline.save()

            return redirect('gas_filling:order_show', pk=order.id)
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

    if order.status == 'CLOSED' and order.fillings.exists():
        order.status = 'IN_PROGRESS'
        order.save()

    fillings = order.fillings.all().order_by('order_line', 'filling_number')
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
    stillages = Stillage.objects.filter(filling=filling).order_by("stillage_num")
    context = {
        'filling': filling,
        'stillages': stillages,
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
    elif not filling.recycle_num:
        return redirect('gas_filling:gas_filling_recyclenum', pk=filling.id)
    elif not filling.heel_weight:
        return redirect('gas_filling:gas_filling_heelweight', pk=filling.id)
    elif not filling.end_weight:
        return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
    else:
        return redirect('gas_filling:gas_filling', pk=filling.order.id)

def order_status(request, pk):
    order = Order.objects.get(pk=pk)    

    if request.method == 'POST':
        action = request.POST.get("action")

        if action == "failed" and order.status == "PACKED":
            order.status = "FAILED"

            send_mail(
                f'Order Failed',
                f'Order #{order.id} has failed and needs reworking.'
                f'http://127.0.0.1:8000/gas_filling/{order.id}/',
                secret.FROM_EMAIL,
                [secret.TO_EMAIL],
            )
        else: 
            if order.status == 'OPEN':
                order.status = 'CLOSED'

                send_mail(
                    f'Order Closed',
                    f'Order #{order.id} has been closed.'
                    f'http://127.0.0.1:8000/gas_filling/{order.id}/',
                    secret.FROM_EMAIL,
                    [secret.TO_EMAIL],
                )
            elif order.status == 'IN_PROGRESS':
                order.status = 'PACKED'
                send_mail(
                    f'Order Packed',
                    f'Order #{order.id} has been packed.'
                    f'http://127.0.0.1:8000/gas_filling/{order.id}/',
                    secret.FROM_EMAIL,
                    [secret.TO_EMAIL],
                )
            elif order.status == 'PACKED':
                order.status = 'PASSED'
                send_mail(
                    f'Order Passed',
                    f'Order #{order.id} has passed QA testing.'
                    f'http://127.0.0.1:8000/gas_filling/{order.id}/',
                    secret.FROM_EMAIL,
                    [secret.TO_EMAIL],
                )
            elif order.status == 'PASSED' or order.status == 'REWORKED':
                order.status = 'FINISHED'
                send_mail(
                    f'Order Finished',
                    f'Order #{order.id} has been completed.'
                    f'http://127.0.0.1:8000/gas_filling/{order.id}/',
                    secret.FROM_EMAIL,
                    [secret.TO_EMAIL],
                )                
            elif order.status == 'FAILED':
                order.status = 'REWORKED'
                send_mail(
                    f'Order Reworked',
                    f'Order #{order.id} has been reworked.'
                    f'http://127.0.0.1:8000/gas_filling/{order.id}/',
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
            orderline.line_number = order.order_lines.count() + 1
            orderline.save()
            return redirect('gas_filling:order_show', order_id)
    else:
        form = OrderLineForm()

    return render(request, 'gas_filling/orderline_create.html', {'form': form, 'order': order})


def orderline_edit(request, orderline_id):
    orderline = get_object_or_404(OrderLine, id=orderline_id)
    order = orderline.order

    if request.method == 'POST':
        form = OrderLineForm(request.POST, instance=orderline)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:order_show', pk=order.id)
    else:
        form = OrderLineForm(instance=orderline)

    context = {
        'order': order,
        'form': form,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/orderline_edit.html', context)


def new_batch(request, pk, prev_batch):
    filling = get_object_or_404(Filling, pk=pk)
    order = filling.order
    current_batch_num = filling.batch_num

    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        start_weight = request.POST.get('start_weight')

        if prev_batch:
            prev_batch_obj, created = Batch.objects.get_or_create(
            batch_num=prev_batch,
            parent_order=order,
            defaults={"start_weight": 0}
        )
        prev_batch_obj.end_weight = end_weight
        prev_batch_obj.save()

        Batch.objects.get_or_create(
            batch_num=current_batch_num,
            parent_order=order,
            defaults={"start_weight": start_weight, "end_weight": 0}
        )

        return redirect('gas_filling:gas_filling_recyclenum', pk=filling.id)

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

def new_recycle(request, pk, prev_recycle):
    filling = get_object_or_404(Filling, pk=pk)
    order = filling.order
    current_recycle_num = filling.recycle_num

    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        start_weight = request.POST.get('start_weight')
        
        if prev_recycle:
            prev_recycle_obj, created = Recycle.objects.get_or_create(
            recycle_num=prev_recycle,
            parent_order=order,
            defaults={"end_weight": 0}
        )
        prev_recycle_obj.start_weight = start_weight
        prev_recycle_obj.save()

        Recycle.objects.get_or_create(
            recycle_num=current_recycle_num,
            parent_order=order,
            defaults={"start_weight": 0, "end_weight": end_weight}
        )

        return redirect('gas_filling:gas_filling_heelweight', pk=filling.id)

    context = {
        'filling': filling,
        'recycle_num': current_recycle_num,
        'order': order,
        'prev_recycle': prev_recycle,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/new_recycle.html', context)

def recycle_list(request):
    recycles = Recycle.objects.all().order_by('-id')
    context = {
        'recycles': recycles,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/recycle_list.html', context)

def pdf_create(request):
    document = []

    document.append(Spacer(1, 20))
    document.append(Paragraph('Summary of Orders and Batches', ParagraphStyle(name='Aloy', fontfamily="Helvetica", fontSize=16, alignment=TA_CENTER)))
    document.append(Spacer(1, 30))

    def organiseOrder(order):
        row = [None] * 8
        row[0] = order.order_number
        row[1] = order.customer
        if order.packer_comments:
            row[2] = order.packer_comments
        else:
            row[2] = None
        if order.analyst_comments:
            row[3] = order.analyst_comments
        else:
            row[3] = None
        if order.qc_instruction:
            row[4] = order.qc_instruction
        else:
            row[4] = None
        row[5] = order.fill_type
        row[6] = str(order.created_time)
        row[7] = order.status
        return row
    
    def organiseFilling(filling):
        row = [None] * 12
        row[0] = id
        row[1] = filling.order.order_number
        row[2] = filling.cylinder.barcodeid
        row[3] = filling.cylinder_time
        row[4] = filling.batch_num
        row[5] = filling.heel_weight
        row[6] = filling.heel_time
        row[7] = filling.cylinder.tare
        row[8] = filling.connection_weight
        row[9] = filling.end_weight
        row[10] = filling.pulled_weight
        row[11] = filling.fill_weight
        return row


    def organiseBatch(batch):
        row = [None] * 4
        row[0] = batch.batch_num
        row[1] = batch.parent_order.order_number
        row[2] = batch.start_weight
        row[3] = batch.end_weight
        return row


    ### order table ###
    table_columns = [None] * (len(Order.objects.all())+1)
    table_columns[0] = ["Num", "Customer", "Packer Comments", "Analyst Comments", "Packaging Instruction" "Fill Type", "Time Created", "Status"]
    count = 1

    for order in Order.objects.all():
        table_columns[count] = organiseOrder(order)
        count += 1

    t = Table(table_columns, colWidths=[40, 100, 120, 60, 60, 70])

    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    document.append(t)
    document.append(Spacer(1,40))
    ### ### ###


    ### filling table ###
    table_columns = [None] * (len(Filling.objects.all())+1)
    table_columns[0] = ["id", "Order", "Cylinder", "Time", "Batch Number", "Heel Weight", "Heel Time", "Tare Weight", "Connection Weight", "End Weight","Pulled Weight", "Fill Weight"]
    count = 1

    for filling in Filling.objects.all():
        table_columns[count] = organiseFilling(filling)
        count += 1

    t = Table(table_columns, colWidths=[90, 100, 60, 70, 70, 70, 70, 70, 70, 70, 70, 70])

    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    document.append(t)
    document.append(Spacer(1,40))
    ### ### ###


    ### batch table ###
    table_columns = [None] * (len(Batch.objects.all())+1)
    table_columns[0] = ["Num", "Parent Order", "Start Weight", "End Weight"]
    count = 1

    for batch in Batch.objects.all():
        table_columns[count] = organiseBatch(batch)
        count += 1

    t = Table(table_columns, colWidths=[40, 100, 120, 60, 60, 70])

    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    document.append(t)
    document.append(Spacer(1,40))
    ### ### ###

    SimpleDocTemplate('OrdersBatches.pdf', pagesize=A4, rightMargin=12, leftMargin=12, topMargin=12, bottomMargin=6).build(document)

    context = {
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/pdf_create.html', context)