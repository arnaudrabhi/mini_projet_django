from django import forms

from .enums import BudgetChoices, RoomChoices
from .models import Equipment, Teacher, Accessory, Purchase


# Teacher utilisé pour représenter la salle de stockage pour le holder de l'équipement
storage_holder, created = Teacher.objects.get_or_create(email='storage@example.com',
                                                        defaults={'first_name': 'Storage', 'last_name': 'Room'})


class EquipmentForm(forms.ModelForm):
    from_budget = forms.ChoiceField(choices=[(choice.name, choice.value) for choice in BudgetChoices], required=False)
    purchase_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = Equipment
        fields = ['name', 'location_room', 'owner', 'holder', 'accessories']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.purchase_form = PurchaseForm(*args, **kwargs)
        self.user = user

        if not self.instance.pk and not self.user.is_staff:
            self.fields['location_room'].initial = RoomChoices.STORAGE.name
            self.fields['location_room'].widget.attrs['readonly'] = True

    def is_valid(self):
        return super().is_valid() and self.purchase_form.is_valid()

    def clean_owner(self):
        owner = self.cleaned_data['owner']
        if owner == 'lycee':
            return storage_holder.id
        return owner

    def save(self, commit=True):
        equipment = super().save(commit=commit)
        if commit:
            purchase = self.purchase_form.save(commit=False)
            purchase.equipment = equipment
            purchase.save()
        return equipment


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['from_budget', 'purchase_date']


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['civility', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['password'].required = False

    def clean_password(self):
        password = self.cleaned_data.get('password')
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and not password:
            return instance.password
        return password


class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['name', 'equipment', 'condition', 'comment']

    def save(self, commit=True):
        accessory = super().save(commit=False)

        if commit:
            accessory.save()

        return accessory


class EquipmentTransferForm(forms.Form):
    storage_holder, created = Teacher.objects.get_or_create(email='storage@example.com',
                                                            defaults={'first_name': 'Storage', 'last_name': 'Room'})

    old_holder = forms.ModelChoiceField(queryset=Teacher.objects.all(), label='Ancien Titulaire')
    new_holder = forms.ModelChoiceField(queryset=Teacher.objects.exclude(id=storage_holder.id), label='Nouveau Titulaire')
    are_accessories_present = forms.BooleanField(required=False, label='Accessoires Présents')
    comment = forms.CharField(widget=forms.Textarea, label='État des accessoires')
    change_reason = forms.CharField(widget=forms.Textarea, label='Raison du Changement')
    location = forms.CharField(max_length=255, label='Emplacement')

    def clean(self):
        cleaned_data = super().clean()
        old_holder = cleaned_data.get('old_holder')
        new_holder = cleaned_data.get('new_holder')

        if old_holder == new_holder:
            self.add_error('new_holder', "Le nouveau titulaire doit être différent de l'ancien titulaire.")


class RetrieveEquipmentForm(forms.Form):
    comment = forms.CharField(label="Commentaire", widget=forms.Textarea)
    are_accessories_present = forms.BooleanField(label="Accessoires présents", required=False)
    holding_change_date = forms.DateField(label="Date de récupération", widget=forms.DateInput(attrs={'type': 'date'}))
    change_reason = forms.CharField(label="Raison du changement", widget=forms.Textarea)
    location = forms.ChoiceField(label="Emplacement", choices=[(choice.value, choice.value) for choice in RoomChoices])

