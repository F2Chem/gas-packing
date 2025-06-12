from django import forms
from .models import Filling


class FillingForm(forms.ModelForm):
    class Meta:
        model = Filling
        fields = ['cylinder', 'order', 'weight']
        widgets = {
            'cylinder': forms.TextInput(),
            'order': forms.TextInput(),
            'weight': forms.TextInput(),
        }

 

    