from django import forms
from .models import Filling, Cylinder, Order


class FillingForm(forms.ModelForm):
    class Meta:
        model = Filling
        fields = ['cylinder', 'batch_num', 'tare_weight', 'end_weight']


class CylinderForm(forms.ModelForm):
    class Meta:
        model = Cylinder
        fields = ['barcodeid', 'heel', 'test_date', 'comments']
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }


class OrderForm(forms.ModelForm):

    CYLINDER_SIZES = [
        ("Big", "Big"),
        ("Medium", "Medium"),
        ("Small", "Small"),
    ]
    PRODUCTS = [
        ("Pfluero", "Pfluero"),
        ("Carbon", "Carbon"),
        ("Chemicals", "Chemicals"),
    ]
    
    cylinder_size = forms.ChoiceField(
        choices=CYLINDER_SIZES,
        required=False,
        label="Cylinder Size",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    products = forms.ChoiceField(
        choices=PRODUCTS,
        required=False,
        label="Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Order
        fields = ['customer', 'comments', 'fill_type', 'email_comments', 'fill_size', 'num_of_cylinders', 'cylinder_size', 'products']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
            'email_comments': forms.Textarea(attrs={'rows': 3}),
            }