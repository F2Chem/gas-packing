from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from django.contrib.auth.decorators import permission_required
from django.utils.timezone import now
from django.core.mail import send_mail
import secret
from .forms import FillingForm, CylinderForm, OrderForm
from .models import Filling, Cylinder, Order


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

    return render(request, 'gas_filling/filling.html', {'order': order})


def gas_filling_batchnum(request, pk):
    filling = Filling.objects.get(pk=pk)

    last_filling = Filling.objects.filter(order=filling.order).exclude(id=filling.id).order_by('-id').first()
    last_batch_num = last_filling.batch_num if last_filling else ''

    if request.method == 'POST':
        batch_num = request.POST.get('batch_num')
        if batch_num:
            filling.batch_num = batch_num
            filling.save()
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
            return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
    return render(request, 'gas_filling/filling_tare.html', {'filling': filling})


def gas_filling_endweight(request, pk):
    filling = Filling.objects.get(pk=pk)

    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        if end_weight:
            filling.end_weight = end_weight
            filling.end_time = now()
            filling.save()
            return redirect('gas_filling:gas_filling_filling', pk=filling.order.id)
    return render(request, 'gas_filling/filling_end.html', {'filling': filling})

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
    orders = Order.objects.all().order_by('id')
    return render(request, 'gas_filling/order_list.html', {'orders': orders})


def order_create(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save()

            send_mail(
                'New Order',
                f'Order #{order.id} has been created.',
                secret.FROM_EMAIL,
                [secret.TO_EMAIL],
            )

            return redirect('gas_filling:order_list')
    else:
        order_form = OrderForm()

    return render(request, 'gas_filling/order_create.html', {'form': order_form})


def order_show(request, pk):
    order = Order.objects.get(pk=pk)
    fillings = order.fillings.all()
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