from django import forms
from .models import Equipment, Teacher, Accessory


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'location_room', 'owner', 'holder', 'accessories']


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['civility', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }


class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['name', 'equipment', 'condition', 'comment']