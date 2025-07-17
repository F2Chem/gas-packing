
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from django.contrib.auth.decorators import permission_required
from django.utils.timezone import now
from django.core.mail import send_mail
import secret
from .forms import FillingForm, CylinderForm, OrderForm
from .models import Filling, Cylinder, Order, Batch

def home(request):
    return render(request, 'gas_filling/index.html')


def cylinder_index(request):
    return redirect('gas_filling:gas_filling_filling')

def cylinder_view(request):
    return redirect('gas_filling:gas_filling_filling')

def cylinder_edit(request):
    return redirect('gas_filling:gas_filling_filling')


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

    return render(request, 'gas_filling/filling.html', {'order': order, 'filling_number': filling_number})


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

    return render(request, 'gas_filling/filling_batch.html', {'filling': filling, 'last_batch_num' : last_batch_num})


def gas_filling_tareweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        tare_weight = request.POST.get('tare_weight')
        if tare_weight:
            filling.tare_weight = tare_weight
            filling.tare_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_connectionweight', pk=filling.id)
    return render(request, 'gas_filling/filling_tare.html', {'filling': filling})

def gas_filling_connectionweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        connection_weight = request.POST.get('connection_weight')
        if connection_weight:
            filling.connection_weight = connection_weight
            filling.connection_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
    return render(request, 'gas_filling/filling_connections.html', {'filling': filling})

def gas_filling_endweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        if end_weight:
            filling.end_weight = end_weight
            filling.end_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_pulledweight', pk=filling.id)
    return render(request, 'gas_filling/filling_end.html', {'filling': filling})

def gas_filling_pulledweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        pulled_weight = request.POST.get('pulled_weight')
        if pulled_weight:
            filling.pulled_weight = pulled_weight
            filling.pulled_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_filling', pk=filling.order.id)
    return render(request, 'gas_filling/filling_pulled.html', {'filling': filling})

def gas_filling_table(request):
    all_fillings = Filling.objects.all().order_by('-end_time')
    return render(request, 'gas_filling/filling_table.html', {'all_fillings': all_fillings})

def gas_filling_home(request):
    return render(request, 'gas_filling/home.html')

def cylinder_list(request):
    cylinders = Cylinder.objects.all().order_by('id')
    return render(request, 'gas_filling/list.html', {'cylinders': cylinders})

def cylinder_show(request, pk):
    cylinder = Cylinder.objects.get(pk=pk)
    return render(request, 'gas_filling/show.html', {'cylinder': cylinder})

def cylinder_edit(request, pk):
    cylinder = Cylinder.objects.get(pk=pk)
    if request.method == 'POST':
        form = CylinderForm(request.POST, instance=cylinder)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:cylinder_list')
    else:
        form = CylinderForm(instance=cylinder)
    return render(request, 'gas_filling/edit.html', {'form': form})

def cylinder_create(request):
    if request.method == 'POST':
        form = CylinderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:gas_filling_home')
    else:
        form = CylinderForm()

    return render(request, 'gas_filling/create.html', {'form': form})


def order_list(request):
    orders = Order.objects.all().order_by('completed', 'id')
    return render(request, 'gas_filling/order_list.html', {'orders': orders})


def order_create(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save()

            send_mail(
                f'Order #{order.id} has been created.',
                f'Customer: {order.customer}. Comments: {order.email_comments}.',
                secret.FROM_EMAIL,
                [secret.TO_EMAIL],
            )

            return redirect('gas_filling:order_list')
    else:
        order_form = OrderForm()

    return render(request, 'gas_filling/order_create.html', {'form': order_form})


def order_show(request, pk):
    order = Order.objects.get(pk=pk)
    fillings = order.fillings.all().order_by('id')
    return render(request, 'gas_filling/order_show.html', {'order': order, 'fillings': fillings})



def order_edit(request, pk):
    order = Order.objects.get(pk=pk)
    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            order_form.save()
            return redirect('gas_filling:order_list')
    else:
        order_form = OrderForm(instance=order)
    return render(request, 'gas_filling/order_edit.html', {'form': order_form, 'order': order})


def filling_show(request, pk):
    filling = get_object_or_404(Filling, pk=pk)
    return render(request, 'gas_filling/filling_show.html', {'filling': filling})

def filling_edit(request, pk):
    filling = Filling.objects.get(pk=pk)
    if request.method == 'POST':
        form = FillingForm(request.POST, instance=filling)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:filling_show', pk=filling.id)
    else:
        form = FillingForm(instance=filling)
    return render(request, 'gas_filling/filling_edit.html', {'form': form, 'filling': filling})

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

def order_complete(request, pk):
    order = Order.objects.get(pk=pk)
    if request.method == 'POST':
        order.completed = True
        order.save()
        send_mail(
                f'Order Finished.',
                f'Order #{order.id} has been marked as completed.',
                secret.FROM_EMAIL,
                [secret.TO_EMAIL],
            )
        return redirect('gas_filling:order_list')
    return render(request, 'gas_filling/order_complete.html', {'order': order})


def order_test(request):
    print('In order_test')
    raise Exception("Error!")


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

    return render(request, 'gas_filling/new_batch.html', {'filling': filling, 'batch_num': current_batch_num, 'order': order,'prev_batch': prev_batch})

def batch_list(request):
    batches = Batch.objects.all().order_by('-id')
    return render(request, 'gas_filling/batch_list.html', {'batches': batches})
