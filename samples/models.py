import re
import csv
import datetime

from django.db import models

from util.util import *

# IMPORTANT
# This is just a stub. If you edit it, let AKJ know so the original can be modified 








"""
Represents one substance that we produce as a final product
It is probably okay to have the data only editable via the admin panel
"""
class Product(TimeStampMixin):
    name = models.CharField(blank=True, null=True)
    identifier = models.CharField(blank=True, null=True)
    alt_names = models.CharField(blank=True, null=True)
    pfc_id = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    sample_log_customs_tariff_id = models.IntegerField(blank=True, null=True)
    hazards = models.TextField(blank=True, null=True)
    subject_to_export_license = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sample_log_products'


    # Find a product, however the user specifies it
    # Unit tested
    def search(term):
        # first strip out the extaneous stuff
        for s in  ['cern', 'tech', 'hp', '93%', 'final', 'product', 'crudes', r'\(', r'\)']:#, r'\-$']:
            term = re.sub(s, '', term)
        term = term.upper().strip()        
        
        if not term:
            return None
        
        search_args = [
          {'name':term},
          {'identifier':term},
          {'identifier':'FLUTEC ' + term},
          {'identifier__icontains':term},
          {'name__icontains':term},
          {'alt_names__icontains':term},
        ]
        
        for args in search_args:
            p = Product.objects.filter(**args).first()
            if p:
                return p

        return None


        
"""
A specification. One product can have several specifications
It is probably okay to have the data only editable via the admin panel
"""
class Spec(TimeStampMixin):
    sample_log_product = models.ForeignKey(Product, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField()  # Needs to be in the for "QCS 102"
    product_name = models.CharField(blank=True, null=True)
    subname = models.CharField(blank=True, null=True) # Optional, eg "Tracer grade"
    link = models.CharField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sample_log_specs'


    def __str__(self):
        return f'{self.product_name} ({self.name})'

    def full_name(self):
        return self.__str__()


    def tg_specs():
        return Spec.objects.filter(product_name__startswith="FLUTEC TG").order_by('product_name')

    def pp_specs():
        return Spec.objects.filter(product_name__startswith="FLUTEC PP").order_by('product_name')

    def cn_specs():
        return Spec.objects.filter(product_name__startswith="Perfluoro").order_by('product_name')

    def other_specs():
        return Spec.objects.exclude(product_name__startswith="Perfluoro").exclude(product_name__startswith="FLUTEC PP").exclude(product_name__startswith="FLUTEC TG").order_by('product_name')







