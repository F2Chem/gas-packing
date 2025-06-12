from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from django.contrib.auth.decorators import permission_required
from .forms import FillingForm
from .models import Filling


def home(request):
    return render(request, 'gas_filling/index.html')


def cylinder_index(request):
    return redirect('/gas_filling/gas_filling/')

def cylinder_view(request):
    return redirect('/gas_filling/gas_filling/')

def cylinder_edit(request):
    return redirect('/gas_filling/gas_filling/')

def gas_filling(request):
    if request.method == 'POST':
        if 'submit' in request.POST:
            form = FillingForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('gas_filling:gas_filling')
            else:
                print(form.errors)
        elif 'clear' in request.POST:
            form = FillingForm()
    else:
        form = FillingForm()
    return render(request, 'gas_filling/filling.html', {'form': form})
