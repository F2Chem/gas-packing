from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
from util.util import *
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta



class Cylinder(models.Model):
    id = models.AutoField(primary_key=True)
    barcodeid = models.CharField(max_length=50, default=0, blank=True, null=True)
    heel = models.FloatField(default=0, blank=True, null=True)
    test_date = models.DateField(blank=True, null=True)
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
    customer = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    packaging_instruction = models.TextField(blank=True, null=True)
    field_instruction = models.TextField(blank=True, null=True)
    fill_type = models.CharField(max_length=50, blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    timestampin = TimeStampMixin

    STATUSES = [
        ('OPEN', 'Open'),                            # Sales department are in the process of creating
        ('IN_PROGRESS', 'In Progress'),              # Sales dept have finalised, and it is in the hands of the packager
        ('PACKED', 'Packed'),                        # Package has said it is done, now in hands of QC
        ('PASSED', 'Passed'),                        # QC have passed it
        ('FAILED', 'Failed'),                        # QC have failed it, and more work required by packager
        ('REWORKED', 'Reworked'),                    # Package has said it is done, now in hands of QC
        ('FINISHED', 'Finished'),                    #  Packager has completed all paper work, all done
    ]
    
    status = models.CharField(max_length=11, choices=STATUSES, default='OPEN')

    class Meta:
        db_table = 'gas_filling_orders'

    @property
    def total_fill_weight(self):
        return sum(filling.fill_weight for filling in self.fillings.all())

    @property
    def total_fills(self):
        return self.fillings.count()

    @property
    def total_orderlines(self):
        return self.order_lines.count()

        
    def reset():
        Filling.objects.all().delete()
        Order.objects.all().delete()


class OrderLine(models.Model):
    CYLINDER_TYPES = [
        ('STANDARD', 'Standard'),
        ('STILLAGE', 'Stillage'),
        ('TUBE_TRAILER', 'Tube Trailer'),
        ('ISOTANK', 'Isotank'),
    ]
    CYLINDER_SIZES = [
        ("BIG", "Big"),
        ("MEDIUM", "Medium"),
        ("SMALL", "Small"),
    ]
    PRODUCTS = [
        ("PFLUERO", "Pfluero"),
        ("CARBON", "Carbon"),
        ("CHEMICALS", "Chemicals"),
    ]
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_lines')
    product = models.CharField(choices=PRODUCTS, max_length=50)
    cylinder_size = models.CharField(choices=CYLINDER_SIZES, max_length=50)   
    fill_weight = models.FloatField(default=0, blank=True, null=True)
    num_cylinders = models.IntegerField(blank=True, null=True)
    stillage = models.BooleanField(default=False, blank=True, null=True)
    cylinder_type = models.CharField(max_length=20, choices=CYLINDER_TYPES)
    keep_heel = models.BooleanField(default=False)


class CylinderSet(models.Model):
    id = models.AutoField(primary_key=True)
    order_line = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name='cylinder_sets')



class Filling(models.Model):
    id = models.AutoField(primary_key=True)
    cylinder = models.CharField(max_length=100)
    cylinder_time = models.DateTimeField(null=True, blank=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='fillings')

    batch_num = models.IntegerField(blank=True, null=True)
    batch_time = models.DateTimeField(null=True, blank=True)

    tare_weight = models.FloatField(default=0, blank=True, null=True)
    tare_time = models.DateTimeField(null=True, blank=True)

    connection_weight = models.FloatField(default=0, blank=True, null=True)
    connection_time = models.DateTimeField(null=True, blank=True)

    end_weight = models.FloatField(default=0, blank=True, null=True)
    end_time = models.DateTimeField(null=True, blank=True)

    pulled_weight = models.FloatField(default=0, blank=True, null=True)
    pulled_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'gas_filling_fillings'

    @property
    def fill_weight(self):
        if self.end_weight is not None and self.tare_weight is not None:
            return round(self.end_weight - self.tare_weight, 1)
        return 0.0
    
    @property
    def heel_weight(self):
        if self.cylinder and self.tare_weight is not None:
            cylinder = Cylinder.barcode_search(self.cylinder)
            if isinstance (cylinder, Cylinder):
                return round(self.tare_weight - cylinder.heel, 1)
        return 0.0


class Batch(models.Model):
    id = models.AutoField(primary_key=True)
    batch_num = models.IntegerField(blank=True, null=True)
    parent_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='batches')
    start_weight = models.FloatField(default=0, null=True, blank=True)
    end_weight = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        db_table = 'gas_filling_batches'

