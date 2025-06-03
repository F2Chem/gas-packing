from django.contrib import admin

from .models import *


admin.site.register(Computer)
admin.site.register(Device)
admin.site.register(StaticIpAddress)
admin.site.register(CyberTarget)
admin.site.register(CyberRiskAssessment)

