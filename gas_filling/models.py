from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
from util.util import *
from datetime import datetime
from dateutil.relativedelta import relativedelta



class Cylinder(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    barcodeid = models.CharField(max_length=50, default=0)
    tare = models.FloatField(default=0)
    test_date = models.DateTimeField()
    comments = models.TextField(blank=True, null=True)

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


    class Meta:
        db_table = 'gas_filling_cylinders'


class Order(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    customer = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    fill_in = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'gas_filling_orders'



class Filling(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    cylinder = models.CharField(max_length=100)
    order = models.CharField(max_length=100)
    weight = models.FloatField(default=0)
    time_entered = models.TimeField(auto_now=True)
    status = models.IntegerField(default=0)


    def filling_status(self):
        return self.status
    
    def update_status(self):
        self.status += 1
    

    class Meta:
        db_table = 'cylinders'