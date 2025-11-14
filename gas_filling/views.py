
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max, Case, When, Value, IntegerField
from django.contrib.auth.decorators import permission_required
from django.utils.timezone import now

from datetime import date, timedelta
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

from .forms import FillingForm, CylinderForm, OrderForm, OrderLineForm
from .models import *
from util.util import *



#EMAIL_PACKAGING = ['andy.joel@f2chemicals.com', 'helen.mcnamee@f2chemicals.com', 'Stephen.Cooke@f2chemicals.com']
#EMAIL_QC = ['andy.joel@f2chemicals.com', 'helen.mcnamee@f2chemicals.com', 'Stephen.Cooke@f2chemicals.com', 'Susan.Dodd@f2chemicals.com', 'Deborah.Clack@f2chemicals.com', 'David.Moss@f2chemicals.com']
EMAIL_PACKAGING = ['andy.joel@f2chemicals.com']
EMAIL_QC = ['andy.joel@f2chemicals.com']



#EMAIL_PACKAGING = ['andy.joel@f2chemicals.com', 'helen.mcnamee@f2chemicals.com', 'Stephen.Cooke@f2chemicals.com']
#EMAIL_QC = ['andy.joel@f2chemicals.com', 'helen.mcnamee@f2chemicals.com', 'Stephen.Cooke@f2chemicals.com', 'Susan.Dodd@f2chemicals.com', 'Deborah.Clack@f2chemicals.com', 'David.Moss@f2chemicals.com']
EMAIL_PACKAGING = ['andy.joel@f2chemicals.com']
EMAIL_QC = ['andy.joel@f2chemicals.com']


def gas_filling(request, pk):
    order_line = OrderLine.objects.get(pk=pk)
    order = order_line.order

    fill_progress = (str((order_line.cylinders_somewhat_filled) + 1) + "/" + str(order_line.num_cylinders))

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
    last_filling = Filling.objects.exclude(batch_id__isnull=True).order_by('-id').first()   # !!!
    last_batch_id = last_filling.batch_id if last_filling else 0

    if request.method == 'POST':
        # Look for the given batch. If we have it ...
        # Otherwise need to go to new_batch to create a new one
        batch_number = int(request.POST.get('batch_num'))
        batch = Batch.objects.filter(product=order_line.product, batch_num=batch_number).first()
        if batch:
            filling.batch_id = batch.id
            filling.save()
            return redirect('gas_filling:gas_filling_recyclenum', pk=filling.id)

        else:
            return redirect('gas_filling:gas_filling_newbatch', pk=filling.id, batch_number=batch_number)


    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'last_batch_id': last_batch_id,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_batch.html', context)


def gas_filling_recyclenum(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))
    last_filling = Filling.objects.exclude(recycle_id__isnull=True).order_by('-id').first()
    last_recycle_id = last_filling.recycle_id if last_filling else 0

    if request.method == 'POST':
        recycle_number = int(request.POST.get('recycle_num'))
        recycle = Recycle.objects.filter(product=order_line.product, recycle_num=recycle_number).first()
        if recycle:
            filling.recycle_id = recycle.id
            filling.save()
            return redirect('gas_filling:gas_filling_heelweight', pk=filling.id)

        else:
            return redirect('gas_filling:gas_filling_newrecycle', pk=filling.id, recycle_number=recycle_number)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'last_recycle_id': last_recycle_id,
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
        check_start_weight = request.POST.get('start_weight')

        if check_start_weight:
            start_weight = float(check_start_weight)
        else:
            start_weight = 0.0

        filling.start_weight = start_weight
        filling.start_time = now()
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


def gas_filling_connectionweight(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order
    cylinder = filling.cylinder

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))

    if request.method == 'POST':
        connection_weight = request.POST.get('connection_weight')
        if connection_weight:
            filling.connection_weight = connection_weight
            filling.connection_time = now()
            filling.save()

            difference = round(filling.start_weight - cylinder.tare, 2)

            if filling.order_line.cylinder_type == "STILLAGE":
                return redirect('gas_filling:gas_filling_heelweight_b', pk=filling.id)

            if difference != 0:
                if order_line.keep_heel:
                    return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
                else:
                    return redirect('gas_filling:gas_filling_heelweight_b', pk=filling.id)
        else:
            filling.save()

        return redirect('gas_filling:gas_filling_endweight', pk=filling.id)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'fill_progress': fill_progress,
        'subsections': 'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/filling_connections.html', context)


def gas_filling_heelweight_b(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order
    cylinder = filling.cylinder

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))

    difference = round(filling.start_weight - cylinder.tare, 2)

    if order_line.cylinder_type != "STILLAGE":      
        error_message = ("A heel of " + str(difference) + "kg was detected. This order line does not allow keeping heels. Remove the heel and weigh again.")
    else:
        error_message = ("Now remove stillage heel and weigh again.")

    if request.method == 'POST':
        empty_weight = float(request.POST.get('empty_weight'))
        if empty_weight != filling.empty_weight or order_line.cylinder_type == "STILLAGE":
            filling.empty_weight = empty_weight
            filling.save()
            return redirect('gas_filling:gas_filling_endweight', pk=filling.id)

    context = {
        'filling': filling,
        'order': order,
        'order_line': order_line,
        'cylinder': cylinder,
        'fill_progress': fill_progress,
        'error_message': error_message,
        'subsections': 'gas_filling/subsections.html',
        'target':filling.target_tare_plus_conn
    }
    return render(request, 'gas_filling/filling_heel_b.html', context)


def gas_filling_endweight(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order
    cylinder = filling.cylinder
    #stillage = None

    #if order_line.cylinder_type == "STILLAGE":
    #    stillage, created = Stillage.objects.get_or_create(stillage_num=Stillage.objects.filter(filling=filling).count()-1, filling = filling)

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))
    stillage_progress = None
    connections = filling.connection_weight - filling.start_weight
    target_weight = round(cylinder.tare + order_line.fill_weight + connections, 2)
    print('here')

    if order_line.cylinder_type == "STILLAGE" and filling.filling_number > 1:
        # For a stillage, the previous cylinders
        print('stillage')
        #stillage_progress = (str(Stillage.objects.filter(filling=filling).count()))
        target_weight = round(filling.start_weight + order_line.fill_weight + connections, 2)
    

    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        if end_weight:
            if order_line.cylinder_type == "STILLAGE":
                #stillage.end_weight = end_weight
                #stillage.end_time = now()
                #stillage.save()
                if filling.filling_number < order_line.num_cylinders:
                    # For a stillage you do not pull down until the end
                    #Stillage.objects.get_or_create(stillage_num=Stillage.objects.filter(filling=filling).count(), filling = filling)
                    return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
                #end_weight = stillage.finished_end_weight(filling)
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

    #if order_line.cylinder_type == "STILLAGE":
    #    stillage = Stillage.objects.filter(filling=filling, pulled_time=None).exclude(end_time=None).order_by("end_time").first()

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))
    stillage_progress = None
    connections = filling.connection_weight - filling.start_weight
    target_weight = round(cylinder.tare + order_line.fill_weight + connections, 2)

    if order_line.cylinder_type == "STILLAGE":
        #stillage_progress = (str(order_line.num_cylinders+1-Stillage.objects.filter(filling=filling, pulled_time=None).count()))
        target_weight = round(filling.start_weight + order_line.fill_weight + connections, 2) 

    if request.method == 'POST':
        pulled_weight = request.POST.get('pulled_weight')
        if pulled_weight:
            if order_line.cylinder_type == "STILLAGE":
                #stillage.pulled_weight = pulled_weight
                #stillage.pulled_time = now()
                #stillage.save()

                if filling.filling_number < order_line.num_cylinders:
                    # For stillages, we pull down after all are filled
                    return redirect('gas_filling:gas_filling_pulledweight', pk=filling.id)
                #pulled_weight = stillage.finished_pulled_weight(filling)
                
            filling.pulled_weight = pulled_weight
            filling.pulled_time = now()
            filling.save()
            
            return redirect('gas_filling:gas_filling_finalweight', pk=filling.id)

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


def gas_filling_finalweight(request, pk):
    filling = Filling.objects.get(pk=pk)
    order_line = filling.order_line
    order = order_line.order
    cylinder = filling.cylinder
    stillage = None

    #if order_line.cylinder_type == "STILLAGE":
    #    stillage = Stillage.objects.filter(filling=filling, final_time=None).exclude(pulled_time=None).order_by("pulled_time").first()

    fill_progress = (str(filling.filling_number) + "/" + str(order_line.num_cylinders))
    stillage_progress = None
    target_weight = round(cylinder.tare + order_line.fill_weight, 2)

    if order_line.cylinder_type == "STILLAGE":
        #stillage_progress = str(order_line.num_cylinders + 1 - Stillage.objects.filter(filling=filling, final_time=None).count())
        target_weight = round(filling.start_weight + order_line.fill_weight, 2)

    if request.method == 'POST':
        final_weight = request.POST.get('final_weight')
        if final_weight:
            if order_line.cylinder_type == "STILLAGE":
                #stillage.final_weight = final_weight
                #stillage.final_time = now()
                #stillage.save()

                if filling.filling_number < order_line.num_cylinders:
                    return redirect('gas_filling:gas_filling_finalweight', pk=filling.id)
                #final_weight = stillage.finished_final_weight(filling)

            filling.final_weight = final_weight
            filling.final_time = now()
            filling.save()

            if order_line.all_somewhat_filled:
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
    return render(request, 'gas_filling/filling_final.html', context)

def gas_filling_table(request):
    all_fillings = Filling.objects.all().order_by('-end_time')
    context = {
        'all_fillings': all_fillings, 
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
            When(status='DISPATCHED', then=Value(9)),
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
            if orderline.cylinder_type == "STILLAGE":
                orderline.keep_heel = False
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
    #stillages = Stillage.objects.filter(filling=filling).order_by("stillage_num")
    context = {
        'filling': filling,
        #'stillages': stillages,
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

    if not filling.batch_id:
        return redirect('gas_filling:gas_filling_batchnum', pk=filling.id)
    elif not filling.recycle_id:
        return redirect('gas_filling:gas_filling_recyclenum', pk=filling.id)
    elif not filling.start_weight:
        return redirect('gas_filling:gas_filling_heelweight', pk=filling.id)
    elif not filling.end_weight:
        return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
    else:
        return redirect('gas_filling:gas_filling', pk=filling.order.id)

def abandon_filling(request, pk):
    filling = Filling.objects.get(pk=pk)
    comment = request.POST.get("abandon")
    if len(comment):
        comment = 'No comment given'
    filling.abandoned = comment
    filling.save()    

    return redirect('gas_filling:order_show', pk=filling.order.id)

def order_status(request, pk):
    order = Order.objects.get(pk=pk)  
    warning = None

    if request.method == 'POST':
        action = request.POST.get("action")
        packer_comments = request.POST.get("packer_comments")
        analyst_comments = request.POST.get("analyst_comments")
        import_certificate = request.POST.get("import_certificate")
        export_certificate = request.POST.get("export_certificate") == "on"
        transport_company = request.POST.get("transport_company")


        if action == "failed" and order.status == "PACKED":
            order.status = "FAILED"
            order.analyst_comments = analyst_comments

            subject = "Order Failed"

            text_content = f"""
            Order #{order.order_number} has failed and needs reworking.
            View order here: http://localhost:8000/gas_filling/order/{order.id}/
            """

            html_content = f"""
            <p>Order #{order.order_number} has failed and needs reworking.</p>
            <p><a href="http://localhost:8000/gas_filling/order/{order.id}/">Click here to view the order</a></p>
            """

            email(request, subject, EMAIL_PACKAGING, text_content, html_content)
            
            
        else: 
            if order.status == 'OPEN':
                order.status = 'CLOSED'

                subject = "Order Closed"

                text_content = f"""
                Order #{order.order_number} has been closed.
                View order here: http://localhost:8000/gas_filling/order/{order.id}/
                """

                html_content = f"""
                <p>Order #{order.order_number} has been closed.</p>
                <p><a href="http://localhost:8000/gas_filling/order/{order.id}/">Click here to view the order</a></p>
                """

                email(request, subject, EMAIL_PACKAGING, text_content, html_content)

    
            elif order.status == 'IN_PROGRESS':
                order.status = 'PACKED'
                order.packer_comments = packer_comments

                subject = "Order Packed"

                text_content = f"""
                Order #{order.order_number} has been packed.
                View order here: http://localhost:8000/gas_filling/order/{order.id}/
                """

                html_content = f"""
                <p>Order #{order.order_number} has been packed.</p>
                <p><a href="http://localhost:8000/gas_filling/order/{order.id}/">Click here to view the order</a></p>
                """

                email(request, subject, EMAIL_PACKAGING, text_content, html_content)
                
                
            elif order.status == 'PACKED':
                order.status = 'PASSED'
                order.analyst_comments = analyst_comments

                subject = "Order Passed"

                text_content = f"""
                Order #{order.order_number} has passed QA testing.
                View order here: http://localhost:8000/gas_filling/order/{order.id}/
                """

                html_content = f"""
                <p>Order #{order.order_number} has passed QA testing.</p>
                <p><a href="http://localhost:8000/gas_filling/order/{order.id}/">Click here to view the order</a></p>
                """

                email(request, subject, EMAIL_QC, text_content, html_content)
                
                
            elif order.status == 'PASSED' or order.status == 'REWORKED':
                order.status = 'FINISHED'
                order.import_certificate = import_certificate
                order.export_certificate = export_certificate

                subject = "Order Complete"

                text_content = f"""
                Order #{order.order_number} has been completed.
                View order here: http://localhost:8000/gas_filling/order/{order.id}/
                """

                html_content = f"""
                <p>Order #{order.order_number} has been completed.</p>
                <p><a href="http://localhost:8000/gas_filling/order/{order.id}/">Click here to view the order</a></p>
                """

                email(request, subject, EMAIL_PACKAGING, text_content, html_content)
                
                
            elif order.status == 'FAILED':
                order.status = 'REWORKED'

                subject = "Order Reworked"

                text_content = f"""
                Order #{order.order_number} has been reworked.
                View order here: http://localhost:8000/gas_filling/order/{order.id}/
                """

                html_content = f"""
                <p>Order #{order.order_number} has been reworked.</p>
                <p><a href="http://localhost:8000/gas_filling/order/{order.id}/">Click here to view the order</a></p>
                """
                
                email(request, subject, EMAIL_PACKAGING, text_content, html_content)
                
                
            elif order.status == 'FINISHED':
                order.status = 'DISPATCHED'
                order.transport_company = transport_company

                subject = "Order Dispatched"

                text_content = f"""
                Order #{order.order_number} has been dispatched using {transport_company}.
                View order here: http://localhost:8000/gas_filling/order/{order.id}/
                """

                html_content = f"""
                <p>Order #{order.order_number} has been dispatched using {transport_company}.</p>
                <p><a href="http://localhost:8000/gas_filling/order/{order.id}/">Click here to view the order</a></p>
                """

                email(request, subject, EMAIL_PACKAGING, text_content, html_content)
                
                
        order.save()        
        return redirect('gas_filling:order_list')

    if order.status == "IN_PROGRESS":
        if order.total_cylinders_filled != order.total_cylinders_required:
            warning = "Warning: " + str(order.total_cylinders_filled) + " / " + str(order.total_cylinders_required) + " cylinders are filled."

    context = {
        'order': order,
        'warning': warning,
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
            if orderline.cylinder_type == "STILLAGE":
                orderline.keep_heel = False
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
            if orderline.cylinder_type == "STILLAGE":
                orderline.keep_heel = False
            orderline.save()
            return redirect('gas_filling:order_show', pk=order.id)
    else:
        form = OrderLineForm(instance=orderline)

    context = {
        'order': order,
        'form': form,
        'subsections':'gas_filling/subsections.html',
    }
    return render(request, 'gas_filling/orderline_edit.html', context)


def new_batch(request, pk, batch_number):
    filling = get_object_or_404(Filling, pk=pk)
    
    # The previous batch is the last one of this product
    prev_batch = Batch.objects.filter(
        product=filling.order_line.product,
    ).last()

    if request.method == 'POST':
        if prev_batch:
            end_weight = request.POST.get('end_weight')
            prev_batch.end_weight = end_weight
            prev_batch.save()

        start_weight = request.POST.get('start_weight')
        new_batch, create = Batch.objects.get_or_create(
            batch_num=batch_number,
            parent_order=filling.order_line.order,
            product=filling.order_line.product,
            defaults={"start_weight": start_weight, "end_weight": 0}
        )
        filling.batch_id = new_batch.id
        filling.save()

        return redirect('gas_filling:gas_filling_recyclenum', pk=filling.id)


    context = {
        'filling': filling,
        'batch_num': batch_number,
        'order': filling.order_line.order,
        'prev_batch': prev_batch.batch_num if prev_batch else None,
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

def new_recycle(request, pk, recycle_number):
    filling = get_object_or_404(Filling, pk=pk)

    # The previous batch is the last one of this product
    prev_recycle = Recycle.objects.filter(
        product=filling.order_line.product,
    ).last()

    if request.method == 'POST':
        if prev_recycle:
            end_weight = request.POST.get('end_weight')
            prev_recycle.end_weight = end_weight
            prev_recycle.save()

        start_weight = request.POST.get('start_weight')
        new_recycle, create = Recycle.objects.get_or_create(
            recycle_num=recycle_number,
            parent_order=filling.order_line.order,
            product=filling.order_line.product,
            defaults={"start_weight": start_weight, "end_weight": 0}
        )
        filling.recycle_id = new_recycle.id
        filling.save()

        return redirect('gas_filling:gas_filling_heelweight', pk=filling.id)

    context = {
        'filling': filling,
        'recycle_num': recycle_number,
        'order': filling.order_line.order,
        'prev_recycle': prev_recycle.recycle_num if prev_recycle else None,
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

def get_weight(request):
    #weight_value = 80.80
    weight_value = Weighing.get_last()
    return HttpResponse(weight_value)

def pdf_create(request):
    buffer = BytesIO()
    document = []

    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        name="Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        spaceAfter=12,
    )
    subheading_style = ParagraphStyle(
        name="SubHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    document.append(Spacer(1, 20))
    document.append(Paragraph("Summary of Orders, Fillings and Batches", heading_style))
    document.append(Spacer(1, 20))

    # Orders
    document.append(Paragraph("Orders", subheading_style))
    for order in Order.objects.all():
        text = f"""
        <b>Order #{order.order_number}</b><br/>
        Customer: {order.customer}<br/>
        Packer Comments: {order.packer_comments or "—"}<br/>
        Analyst Comments: {order.analyst_comments or "—"}<br/>
        Packaging Instruction: {order.qc_instruction or "—"}<br/>
        Fill Type: {order.fill_type}<br/>
        Created: {order.created_time}<br/>
        Status: {order.status}
        """
        document.append(Paragraph(text, body_style))
        document.append(Spacer(1, 8))

    # Fillings
    document.append(Paragraph("Fillings", subheading_style))
    for filling in Filling.objects.all():
        text = f"""
        <b>Filling #{filling.id}</b><br/>
        Order: {filling.order.order_number}<br/>
        Cylinder: {filling.cylinder.barcodeid}<br/>
        Time: {filling.cylinder_time}<br/>
        Batch: {filling.batch_number}<br/>
        Start Weight: {filling.start_weight or "—"}<br/>
        Start Time: {filling.start_time or "—"}<br/>
        Tare Weight: {filling.cylinder.tare or "—"}<br/>
        Connection Weight: {filling.connection_weight or "—"}<br/>
        End Weight: {filling.end_weight or "—"}<br/>
        Pulled Weight: {filling.pulled_weight or "—"}<br/>
        Fill Weight: {filling.fill_weight or "—"}
        """
        document.append(Paragraph(text, body_style))
        document.append(Spacer(1, 8))

    # Batches
    document.append(Paragraph("Batches", subheading_style))
    for batch in Batch.objects.all():
        text = f"""
        <b>Batch #{batch.batch_num}</b><br/>
        Parent Order: {batch.parent_order.order_number}<br/>
        Start Weight: {batch.start_weight or "—"}<br/>
        End Weight: {batch.end_weight or "—"}
        """
        document.append(Paragraph(text, body_style))
        document.append(Spacer(1, 8))

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=12,
    )
    pdf.build(document)

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="OrdersBatches.pdf"'


    context = {"subsections": "gas_filling/subsections.html"}
    return response