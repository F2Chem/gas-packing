from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from django.contrib.auth.decorators import permission_required


def index(request):
    return redirect('/gas_filling/gas_filling/')


def cylinder_index(request):
    return redirect('/gas_filling/gas_filling/')

def cylinder_view(request):
    return redirect('/gas_filling/gas_filling/')

def cylinder_edit(request):
    return redirect('/gas_filling/gas_filling/')

