from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
from util.util import *
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta



class Cylinder(models.Model):
    id = models.AutoField(primary_key=True)
    barcodeid = models.CharField(max_length=50, default=0)
    tare = models.FloatField(default=0)
    test_date = models.DateField()
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
        return datetime.today().date() < tolerance


    class Meta:
        db_table = 'gas_filling_cylinders'


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    ordernum = models.CharField(max_length=50, default=0)
    customer = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    fill_type = models.CharField(max_length=50, blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    timestampin = TimeStampMixin

    class Meta:
        db_table = 'gas_filling_orders'

    @property
    def total_fill_weight(self):
        return sum(filling.fill_weight for filling in self.fillings.all())
        
    def reset():
        Filling.objects.all().delete()
        Order.objects.all().delete()


class Filling(models.Model):
    id = models.AutoField(primary_key=True)
    cylinder = models.CharField(max_length=100)
    cylinder_time = models.DateTimeField(null=True, blank=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='fillings')
    order_time = models.DateTimeField(null=True, blank=True)

    batch_num = models.FloatField(default=0, blank=True, null=True)

    tare_weight = models.FloatField(default=0, blank=True, null=True)
    tare_time = models.DateTimeField(null=True, blank=True)

    end_weight = models.FloatField(default=0, blank=True, null=True)
    end_time = models.DateTimeField(null=True, blank=True) 

    class Meta:
        db_table = 'gas_filling_fillings'

    @property
    def fill_weight(self):
        if self.end_weight is not None and self.tare_weight is not None:
            return self.end_weight - self.tare_weight
        return 0.0