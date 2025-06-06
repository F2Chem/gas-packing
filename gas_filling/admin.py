from django.contrib import admin

from .models import Cylinder, Order, Filling

admin.site.register(Cylinder)
admin.site.register(Order)
admin.site.register(Filling)