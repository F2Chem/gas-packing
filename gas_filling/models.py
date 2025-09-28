from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
from util.util import *
from datetime import datetime, date, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta





class Weighing(models.Model):
    #id = models.IntegerField(primary_key=True, db_column='TransactionID')
    #timestamp = models.DateTimeField(db_column='TransactionDateTime')
    #weight = models.DecimalField(max_digits=10, decimal_places=4, db_column='NetWeight')
    id = models.FloatField(primary_key=True, db_column='transactionid')
    timestamp = models.DateTimeField(db_column='TransactionDateTime')
    weight = models.DecimalField(max_digits=10, decimal_places=4, db_column='NetWeight')


    @staticmethod
    def get_last():
        return Weighing.objects.all()[0].weight    
    
    
    def count():
        return Weighing.objects.count()
    
    
    class Meta:
        db_table = 'tbTransactions'
        managed = False




class Cylinder(models.Model):
    id = models.AutoField(primary_key=True)
    barcodeid = models.CharField(max_length=50, default=0, blank=True, null=True, unique=True)
    tare = models.FloatField()
    heel = models.FloatField(default=0, blank=True, null=True)
    test_date = models.DateField()
    comments = models.TextField(blank=True, null=True)
    timestampin = TimeStampMixin
    EXPIRES_AFTER = relativedelta(years=5)
    WARNING_AFTER = relativedelta(years=5, months=-6)

    @staticmethod 
    def barcode_search(barcode):
        try:
            cylinder = Cylinder.objects.get(barcodeid=barcode)
            return cylinder
        except:
            return "barcode error"
        
    
    # don't use cylinder if in 6 months of it's test date, or expired
    def check_in_date(self):
        if datetime.today().date() > self.test_date + self.EXPIRES_AFTER:
            return 2  # expired
        tolerance = self.test_date + self.WARNING_AFTER
        if datetime.today().date() > tolerance:
            return 1  # warning
        return 0  # valid

    @property
    def expiry_date(self):
        return self.test_date + self.EXPIRES_AFTER

    class Meta:
        db_table = 'gas_filling_cylinders'


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=20, blank=False, null=False)
    customer = models.CharField(max_length=50, blank=False, null=False)
    packer_comments = models.TextField(default = "not yet", blank=True, null=True)
    analyst_comments = models.TextField(default = "not yet", blank=False, null=False)
    import_certificate = models.CharField(max_length=20, default = 1, blank=False, null=False)
    export_certificate = models.BooleanField(default=False)
    transport_company = models.CharField(max_length=100, blank=True, null=True, default="")
    packaging_instruction = models.TextField(blank=True, null=True)
    qc_instruction = models.TextField(blank=True, null=True)
    fill_type = models.CharField(max_length=50, blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    timestampin = TimeStampMixin

    STATUSES = [
        ('OPEN', 'Open '),                            # Sales department are in the process of creating
        ('CLOSED', 'Closed '),                        # Sales department have finalised order
        ('IN_PROGRESS', 'In Progress '),              # Order is in the hands of the packager
        ('PACKED', 'Packed '),                        # Package has said it is done, now in hands of QC
        ('PASSED', 'Passed '),                        # QC have passed it
        ('FAILED', 'Failed '),                        # QC have failed it, and more work required by packager
        ('REWORKED', 'Reworked '),                    # Package has said it is done, now in hands of QC
        ('FINISHED', 'Finished '),                    #  Packager has completed all paper work, all done
        ('DISPATCHED', 'Dispatched '),                # Package has been dispatched
    ]

    STATUS_COLOURS = {
    "OPEN": "#fff3cd",
    "CLOSED": "#eca8fd",
    "IN_PROGRESS": "#d4edda",
    "PACKED": "#cce5ff",
    "PASSED": "#a9fbd1",
    "FAILED": "#ffa7a7",
    "REWORKED": "#ebcefa",
    "FINISHED": "#8fffa9",
    "DISPATCHED": "#66c2ff",
}
    
    status = models.CharField(max_length=11, choices=STATUSES, default='OPEN')

    class Meta:
        db_table = 'gas_filling_orders'

    @property
    def total_fill_weight(self):
        return sum(filling.fill_weight for line in self.order_lines.all() for filling in line.fillings.all() if filling.end_weight is not None and filling.end_weight > 0)

    @property
    def total_fills(self):
        return sum(line.fillings.filter(end_weight__isnull=False).exclude(end_weight=0).count() for line in self.order_lines.all())

    @property
    def total_orderlines(self):
        return self.order_lines.count()
        
    @property
    def target_fill(self):
        return sum(line.fill_weight for line in self.order_lines.all())

    @property
    def fillings(self):
        return Filling.objects.filter(order_line__order=self)

    @property
    def total_cylinders_required(self):
        return sum(line.num_cylinders for line in self.order_lines.all())

    @property
    def total_cylinders_filled(self):
        return sum(line.cylinders_filled for line in self.order_lines.all())

    def get_status_colour(self):
        return self.STATUS_COLOURS.get(self.status, "#000000")
       
    # Used for debugging only; excluded from testing
    def reset():   # pragma: no cover
        Filling.objects.all().delete()
        Batch.objects.all().delete()
        OrderLine.objects.all().delete()
        Recycle.objects.all().delete()
        Order.objects.all().delete()


class OrderLine(models.Model):
    CYLINDER_TYPES = [
        ('STANDARD', 'Standard'),
        ('STILLAGE', 'Stillage'),
        ('TUBE_TRAILER', 'Tube Trailer'),
        ('ISOTANK', 'Isotank'),
    ]
    PRODUCTS = [
        ("OCTAFLUOROPROPANE", "Octafluoropropane"),
        ("PERFLUOROBUTANE", "Perfluorobutane"),
    ]
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_lines')
    line_number = models.PositiveIntegerField()
    product = models.CharField(choices=PRODUCTS, max_length=50)
    cylinder_size = models.FloatField(blank=False, null=False)   
    fill_weight = models.FloatField(blank=False, null=False)
    num_cylinders = models.IntegerField(blank=False, null=False)
    cylinder_type = models.CharField(max_length=20, choices=CYLINDER_TYPES)
    keep_heel = models.BooleanField(default=False)

    @property
    def cylinders_filled(self):
        return self.fillings.exclude(final_weight=0).count()
    
    @property
    def cylinders_somewhat_filled(self):
        return self.fillings.count()

    @property
    def all_filled(self):
        if self.cylinder_type == "STILLAGE":
            return self.cylinders_filled > 0
        else:
            return self.cylinders_filled == self.num_cylinders

    @property
    def all_somewhat_filled(self):
        if self.cylinder_type == "STILLAGE":
            return self.cylinders_somewhat_filled > 0
        else:
            return self.cylinders_somewhat_filled == self.num_cylinders


class CylinderSet(models.Model):
    id = models.AutoField(primary_key=True)
    order_line = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name='cylinder_sets')



class Filling(models.Model):
    id = models.AutoField(primary_key=True)
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE, related_name='fillings', null=True, blank=True)
    cylinder_time = models.DateTimeField(null=True, blank=True)

    order_line = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name='fillings')

    batch_num = models.IntegerField(blank=True, null=True)
    batch_time = models.DateTimeField(null=True, blank=True)

    recycle_num = models.IntegerField(blank=True, null=True)
    recycle_time = models.DateTimeField(null=True, blank=True)

    start_weight = models.FloatField(default=0, blank=True, null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    empty_weight = models.FloatField(blank=True, null=True)

    connection_weight = models.FloatField(default=0, blank=True, null=True)
    connection_time = models.DateTimeField(null=True, blank=True)

    end_weight = models.FloatField(default=0, blank=True, null=True)
    end_time = models.DateTimeField(null=True, blank=True)

    pulled_weight = models.FloatField(default=0, blank=True, null=True)
    pulled_time = models.DateTimeField(null=True, blank=True)

    final_weight = models.FloatField(default=0, blank=True, null=True)
    final_time = models.DateTimeField(null=True, blank=True)

    filling_number = models.IntegerField(default=1)

    class Meta:
        db_table = 'gas_filling_fillings'

    @property
    def fill_weight(self):
        if self.final_weight and self.cylinder and self.cylinder.tare:
            return round(self.final_weight - self.cylinder.tare, 1)
        return 0.0
    
    @property
    def net_heel_weight(self):
        if self.cylinder and self.cylinder.tare and self.start_weight is not None:
            return round(self.start_weight - self.cylinder.tare, 1)
        return 0.0

    @property
    def taken_weight(self):
        if self.connection_weight and self.end_weight:
            return round(self.end_weight - self.connection_weight, 1)
        return 0.0
        
    @property
    def recycle_weight(self):
        if self.start_weight and self.empty_weight and self.end_weight and self.pulled_weight:
            return (round(self.start_weight - self.empty_weight, 1) + round(self.end_weight - self.pulled_weight, 1))
        return 0.0
        
    @property
    def pulled_diff_weight(self):
        if self.pulled_weight and self.end_weight:
            return round(self.end_weight - self.pulled_weight, 1)
        return 0.0

    @property
    def order(self):
        return self.order_line.order



class Stillage(models.Model):
    id = models.AutoField(primary_key=True)
    stillage_num = models.IntegerField(blank=True, null=True)
    filling = models.ForeignKey(Filling, on_delete=models.CASCADE, related_name='stillages', null=True, blank=True)

    end_weight = models.FloatField(default=0, blank=True, null=True)
    end_time = models.DateTimeField(null=True, blank=True)

    pulled_weight = models.FloatField(default=0, blank=True, null=True)
    pulled_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'gas_filling_stillages'

    @staticmethod
    def finished_end_weight(filling):
        stillages = Stillage.objects.filter(filling=filling)
        weight = 0
        for stillage in stillages:
            weight += stillage.end_weight
        return weight
    
    @staticmethod
    def finished_pulled_weight(filling):
        stillages = Stillage.objects.filter(filling=filling)
        weight = 0
        for stillage in stillages:
            weight += stillage.pulled_weight
        return weight



class Batch(models.Model):
    id = models.AutoField(primary_key=True)
    batch_num = models.IntegerField(blank=True, null=True, unique=False)
    parent_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='batches')
    start_weight = models.FloatField(default=0, null=True, blank=True)
    end_weight = models.FloatField(default=0, null=True, blank=True)

    @property
    def used_weight(self):
        if self.end_weight is not None:
            return self.start_weight - self.end_weight

    class Meta:
        db_table = 'gas_filling_batches'



class Recycle(models.Model):
    id = models.AutoField(primary_key=True)
    recycle_num = models.IntegerField(blank=True, null=True, unique=False)
    parent_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='recycles')
    start_weight = models.FloatField(default=0, null=True, blank=True)
    end_weight = models.FloatField(default=0, null=True, blank=True)

    @property
    def recycled_weight(self):
        if self.end_weight is not None:
            return self.end_weight - self.start_weight

    class Meta:
        db_table = 'gas_filling_recycles'

