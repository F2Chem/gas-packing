from django.contrib import admin

from .models import *

# Note: Excludes Weighing

admin.site.register(Cylinder)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(CylinderSet)
admin.site.register(Filling)
admin.site.register(Stillage)
admin.site.register(Batch)
admin.site.register(Recycle)