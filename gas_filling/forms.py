from django import forms
from .models import Filling


class FillingForm(forms.ModelForm):
    class Meta:
        model = Filling
        fields = ['cylinder', 'order', 'tare_weight', 'tare_time', 'end_weight', 'end_time']