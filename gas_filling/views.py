from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from django.contrib.auth.decorators import permission_required
from django.utils.timezone import now
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

# def gas_filling(request):
#     if request.method == 'POST':
#         cylinder_id = request.POST.get('cylinder_id')
#         if cylinder_id:
#             request.session['cylinder'] = cylinder_id
#             return redirect('gas_filling:gas_filling_order')
#     return render(request, 'gas_filling/filling.html')

def gas_filling(request, pk):
    order = Order.objects.get(pk=pk)
    if request.method == 'POST':
        cylinder_barcode = request.POST.get('cylinder_id')
        if cylinder_barcode:
            filling = Filling.objects.create(
                cylinder=cylinder_barcode,
                order=order,
                tare_weight=None,
                tare_time=None,
                end_weight=None,
                end_time=None
            )
            filling.save()
            return redirect('gas_filling:gas_filling_tareweight', pk=filling.id)
    return render(request, 'gas_filling/filling.html')

# def gas_filling_order(request):
#     if request.method == "POST":
#         order_num = request.POST.get("order_number")
#         if order_num:
#             request.session["order_number"] = order_num
#             return redirect('gas_filling:gas_filling_tareweight')
#     return render(request, 'gas_filling/filling_order.html')


# def gas_filling_tareweight(request):
#     if request.method == 'POST':
#         tare_weight = request.POST.get('tare_weight')
#         if tare_weight:
#             request.session['tare_weight'] = float(tare_weight)
#             request.session['tare_time'] = now().isoformat()
#             return redirect('gas_filling:gas_filling_endweight')
#     return render(request, 'gas_filling/filling_tare.html')


def gas_filling_tareweight(request, pk):
    if request.method == 'POST':
        tare_weight = request.POST.get('tare_weight')
        if tare_weight:
            filling = Filling.objects.get(id=pk)
            tare_weight = float(tare_weight)
            tare_time = now().isoformat()
            filling.tare_weight = tare_weight
            filling.tare_time = tare_time
            filling.save()
            return redirect('gas_filling:gas_filling_endweight', pk=filling.id)
    return render(request, 'gas_filling/filling_tare.html')

# def gas_filling_endweight(request):
#     if request.method == 'POST':
#         end_weight = request.POST.get('end_weight')
#         if end_weight:
#             Filling.objects.create(
#                 cylinder=request.session.get('cylinder'),
#                 order=request.session.get('order_number'),
#                 tare_weight=request.session.get('tare_weight'),
#                 tare_time=request.session.get('tare_time'),
#                 end_weight=float(end_weight),
#                 end_time=now()
#             )
#             request.session.pop('cylinder', None)
#             request.session.pop('tare_weight', None)
#             request.session.pop('tare_time', None)
#             return redirect('gas_filling:gas_filling_home')
#     return render(request, 'gas_filling/filling_end.html')

def gas_filling_endweight(request, pk):
    if request.method == 'POST':
        end_weight = request.POST.get('end_weight')
        if end_weight:
            filling = Filling.objects.get(id=pk)
            end_weight = float(end_weight)
            end_time = now().isoformat()
            filling.end_weight = end_weight
            filling.end_time = end_time
            filling.save()
            return redirect('gas_filling:order_list')
    return render(request, 'gas_filling/filling_end.html')

def gas_filling_table(request):
    all_fillings = Filling.objects.all().order_by('-end_time')
    return render(request, 'gas_filling/filling_table.html', {'all_fillings': all_fillings})

def gas_filling_home(request):
    return render(request, 'gas_filling/home.html')

def gas_filling_list(request):
    cylinders = Cylinder.objects.all()
    return render(request, 'gas_filling/list.html', {'cylinders': cylinders})

def gas_filling_show(request, pk):
    cylinder = Cylinder.objects.get(pk=pk)
    return render(request, 'gas_filling/show.html', {'cylinder': cylinder})

def gas_filling_edit(request, pk):
    cylinder = Cylinder.objects.get(pk=pk)
    if request.method == 'POST':
        form = CylinderForm(request.POST, instance=cylinder)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:gas_filling_list')
    else:
        form = CylinderForm(instance=cylinder)
    return render(request, 'gas_filling/edit.html', {'form': form})

def gas_filling_create(request):
    if request.method == 'POST':
        form = CylinderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gas_filling:gas_filling_home')
    else:
        form = CylinderForm()

    return render(request, 'gas_filling/create.html', {'form': form})


def order_list(request):
    orders = Order.objects.all()
    return render(request, 'gas_filling/order_list.html', {'orders': orders})


def order_create(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order_form.save()
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

