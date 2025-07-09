from django import forms
from .models import Filling, Cylinder, Order


class FillingForm(forms.ModelForm):
    class Meta:
        model = Filling
        fields = ['cylinder', 'batch_num', 'tare_weight', 'end_weight']


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
        fields = ['customer', 'comments', 'fill_type', 'email_comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
            'email_comments': forms.Textarea(attrs={'rows': 3}),
            }