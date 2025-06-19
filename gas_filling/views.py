from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from django.contrib.auth.decorators import permission_required
from .forms import FillingForm
from .models import Filling, Cylinder, Order


def home(request):
    return render(request, 'gas_filling/index.html')


def cylinder_index(request):
    return redirect('gas_filling:gas_filling_filling')

def cylinder_view(request):
    return redirect('gas_filling:gas_filling_filling')

def cylinder_edit(request):
    return redirect('gas_filling:gas_filling_filling')

def gas_filling(request):
    if request.method == 'POST':
        if 'submit' in request.POST:
            form = FillingForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('gas_filling:gas_filling_home')
            else:
                print(form.errors)
        elif 'clear' in request.POST:
            form = FillingForm()
    else:
        form = FillingForm()
    return render(request, 'gas_filling/filling.html', {'form': form})

def gas_filling_table(request):
    all_fillings = Filling.objects.all().order_by('-time_entered')
    return render(request, 'gas_filling/filling_table.html', {'all_fillings': all_fillings})

def gas_filling_home(request):
    return render(request, 'gas_filling/home.html')

def gas_filling_list(request):
    return render(request, 'gas_filling/list.html')

def gas_filling_show(request):
    return render(request, 'gas_filling/show.html')