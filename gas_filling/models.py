from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
from util.util import *
from datetime import datetime
from dateutil.relativedelta import relativedelta



class Cylinder(models.Model):
    id = models.AutoField(primary_key=True)
    barcodeid = models.CharField(max_length=50, default=0)
    tare = models.FloatField(default=0)
    test_date = models.DateTimeField()
    comments = models.TextField(blank=True, null=True)
    timestampin = TimeStampMixin

    @staticmethod 
    def barcode_search(barcode):
        try:
            cylinder = Cylinder.objects.get(barcodeid=barcode)
            return cylinder
        except:
            return "barcode error"
        
    
    # don't use cylinder if in 6 months of it's test date
    def check_in_date(self):
        tolerance = self.test_date + relativedelta(months=-6)
        return datetime.today().date() < tolerance.date()



class Order(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    fill_in = models.CharField(max_length=50, blank=True, null=True)
    timestampin = TimeStampMixin



class Filling(models.Model):
    id = models.AutoField(primary_key=True)
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    weight = models.FloatField(default=0)
    timestampin = TimeStampMixin