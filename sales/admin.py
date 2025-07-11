from django.contrib import admin

from .models import *

admin.site.register(Zone)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(Instruction)
admin.site.register(SalesEmail)


