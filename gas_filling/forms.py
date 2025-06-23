from django import forms
from .models import Filling
from .models import Cylinder


class FillingForm(forms.ModelForm):
    class Meta:
        model = Filling
        fields = ['cylinder', 'order', 'tare_weight', 'tare_time', 'end_weight', 'end_time']


class CylinderForm(forms.ModelForm):
    class Meta:
        model = Cylinder
        fields = ['barcodeid', 'tare', 'test_date', 'comments']
        widgets = {
            'test_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
