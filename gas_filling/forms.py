from django import forms
from .models import Filling, Cylinder, Order, OrderLine


class FillingForm(forms.ModelForm):
    class Meta:
        model = Filling
        fields = ['cylinder', 'batch_num', 'end_weight']


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
        fields = ['customer', 'order_number', 'comments', 'packaging_instruction', 'qc_instruction']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),  
            'packaging_instruction': forms.Textarea(attrs={'rows': 3}),
            'qc_instruction': forms.Textarea(attrs={'rows': 3}),
            }


class OrderLineForm(forms.ModelForm):
    class Meta:
        model = OrderLine
        fields = ['product', 'cylinder_size', 'cylinder_type', 'fill_weight', 'num_cylinders', 'keep_heel']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'cylinder_type': forms.Select(attrs={'class': 'form-control'}),
            'keep_heel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }