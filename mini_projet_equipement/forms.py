from django import forms

from .enums import BudgetChoices
from .models import Equipment, Teacher, Accessory, Purchase


class EquipmentForm(forms.ModelForm):
    from_budget = forms.ChoiceField(choices=[(choice.name, choice.value) for choice in BudgetChoices], required=False)
    purchase_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = Equipment
        fields = ['name', 'location_room', 'owner', 'holder', 'accessories']

    def save(self, commit=True):
        equipment = super().save(commit=commit)
        if commit:
            from_budget = self.cleaned_data.get('from_budget')
            purchase_date = self.cleaned_data.get('purchase_date')
            if from_budget and purchase_date:
                Purchase.objects.create(equipment=equipment, from_budget=from_budget, purchase_date=purchase_date)
        return equipment


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

    def save(self, commit=True):
        accessory = super().save(commit=False)

        if commit:
            accessory.save()

        return accessory
