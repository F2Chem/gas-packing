from django import forms
from .models import Filling, Cylinder, Order


class FillingForm(forms.ModelForm):
    class Meta:
        model = Filling
        fields = ['cylinder', 'order', 'tare_weight', 'tare_time', 'end_weight', 'end_time']


class CylinderForm(forms.ModelForm):
    class Meta:
        model = Cylinder
        fields = ['barcodeid', 'tare', 'test_date', 'comments']
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'comments', 'fill_in']
        widgets = {'comments': forms.Textarea(attrs={'rows': 3}),}