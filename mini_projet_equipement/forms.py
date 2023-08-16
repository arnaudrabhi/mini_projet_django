from django import forms
from .models import Equipment


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'location_room', 'owner', 'holder', 'accessories']
