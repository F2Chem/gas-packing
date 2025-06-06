from django.db import models
from django.conf import settings
from django.utils.html import strip_tags

class Cylinder(models.Model):
    num = models.CharField(max_length=200)
    tare = models.FloatField(default=0)
    test_date = models.DateTimeField("test date")
    comments = models.TextField(blank=True, null=True)

class Order(models.Model):
    customer = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    fill_in = models.CharField(max_length=50, blank=True, null=True)


class Filling(models.Model):
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    weight = models.FloatField(default=0)
    time_entered = models.TimeField(auto_now=True)