from enum import Enum

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone

from .enums import BudgetChoices, RoomChoices
from .models import Equipment, Teacher, Accessory, HolderHistory, Purchase
from .forms import EquipmentForm, TeacherForm, AccessoryForm, EquipmentTransferForm, RetrieveEquipmentForm
from django.shortcuts import render

# Teacher utilisé pour représenter la salle de stockage pour le holder de l'équipement
storage_holder, created = Teacher.objects.get_or_create(email='storage@example.com',
                                                        defaults={'first_name': 'Storage', 'last_name': 'Room'})


def home(request):
    if request.user.is_authenticated:

        total_equipment_count = Equipment.objects.count()
        total_teacher_count = Teacher.objects.count()
        total_accessory_count = Accessory.objects.count()
        user_equipment = Equipment.objects.filter(holder=request.user)

        context = {
            'total_equipment_count': total_equipment_count,
            'total_teacher_count': total_teacher_count,
            'total_accessory_count': total_accessory_count,
            'user_equipment': user_equipment,
        }
    else:
        context = {}

    return render(request, 'home.html', context)


class TeacherLoginView(LoginView):
    template_name = 'teacher/teacher_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')


class TeacherLogoutView(LogoutView):
    next_page = reverse_lazy('teacher_login')


class Filter(Enum):
    HOLDER = 'Possesseur'
    OWNER = 'Propriétaire'
    BUDGET = 'Budget'


@login_required
def equipment_list(request):
    selected_filter = request.GET.get('filter_by', '')
    selected_value = request.GET.get('filter_value', '')
    selected_order = request.GET.get('order_by', '')

    equipments = Equipment.objects.all()

    rented_equipments = Equipment.objects.exclude(holder_id=storage_holder.id)
    non_rented_equipments = Equipment.objects.filter(holder_id=storage_holder.id)

    if selected_filter and selected_value:
        equipments = apply_filter(equipments, selected_filter, selected_value)


    all_holders = list(Teacher.objects.values_list('id', flat=True).distinct())
    all_owners = list(Teacher.objects.values_list('id', flat=True).distinct())
    teacher_id_to_name = {teacher.id: f"{teacher.civility} {teacher.first_name} {teacher.last_name}" for teacher in
                          Teacher.objects.all()}

    all_budgets = [
        BudgetChoices.CURRENT_YEAR.value,
        BudgetChoices.PROJECTS.value,
        BudgetChoices.EXCEPTIONAL_FUNDING.value,
    ]

    context = {
        'equipments': equipments,
        'selected_filter': selected_filter,
        'selected_value': selected_value,
        'selected_order': selected_order,
        'all_holders': all_holders,
        'all_owners': all_owners,
        'all_budgets': all_budgets,
        'teacher_id_to_name': teacher_id_to_name,
        'rented_equipments': rented_equipments,
        'non_rented_equipments': non_rented_equipments,
    }

    return render(request, 'equipment/equipment_list.html', context)


def apply_filter(queryset, selected_filter, selected_value):
    if selected_filter == 'holder':
        return queryset.filter(holder_id=selected_value)
    elif selected_filter == 'owner':
        return queryset.filter(owner_id=selected_value)
    elif selected_filter == 'budget':
        if selected_value == BudgetChoices.CURRENT_YEAR.value:
            return queryset.filter(purchase__from_budget='Current Year')
        elif selected_value == BudgetChoices.PROJECTS.value:
            return queryset.filter(purchase__from_budget='Projects')
        elif selected_value == BudgetChoices.EXCEPTIONAL_FUNDING.value:
            return queryset.filter(purchase__from_budget='Exceptional Funding')
    return queryset


def apply_order(queryset, selected_order):
    if selected_order == 'name':
        return queryset.order_by('name')
    elif selected_order == 'location_room':
        return queryset.order_by('location_room')
    return queryset


@login_required
def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    return render(request, 'equipment/equipment_detail.html', {'equipment': equipment})


@login_required
def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.user, request.POST)
        form.instance.location_room = RoomChoices.STORAGE.name  # Set default value here
        if form.instance.owner == 'lycee':
            form.instance.owner = storage_holder

        if form.is_valid():

            form.save()
            return redirect('equipment_list')
        else:
            print(form.errors)
    else:
        initial_location = RoomChoices.STORAGE.name
        form = EquipmentForm(request.user, initial={'location_room': initial_location})
        form.instance.location_room = RoomChoices.STORAGE.name

    form.fields['location_room'].choices = [(choice.value, choice.name) for choice in RoomChoices]
    form.fields['location_room'].widget.attrs['readonly'] = True

    form_title = "Enregistrer un nouvel équipement"
    context = {'form': form, 'form_title': form_title}
    return render(request, 'equipment/equipment_form.html', context)


@login_required
def equipment_update(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    purchase = Purchase.objects.filter(equipment=equipment).first()

    if request.method == 'POST':
        form = EquipmentForm(request.user, request.POST, instance=equipment)
        if not form.is_valid():
            print(form.errors)
        if form.is_valid():
            owner = form.cleaned_data['owner']
            if owner == 'Lycée':
                form.instance.owner = None
            form.save()
            print("ici")
            return redirect('equipment_list')
    else:
        initial_data = {
            'from_budget': purchase.from_budget if purchase else None,
            'purchase_date': purchase.purchase_date if purchase else None,
        }
        form = EquipmentForm(request.user, instance=equipment, initial=initial_data)

    form.fields['location_room'].choices = [(choice.value, choice.name) for choice in RoomChoices]

    form_title = "Éditer un équipement"
    context = {'form': form, 'form_title': form_title}

    return render(request, 'equipment/equipment_form.html', context)


@login_required
def equipment_delete(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        equipment.delete()
        return redirect('equipment_list')
    return render(request, 'equipment/equipment_confirm_delete.html', {'equipment': equipment})


@login_required
def equipment_transfer_view(request, equipment_id):
    equipment = Equipment.objects.get(pk=equipment_id)

    if equipment.holder != request.user:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    if request.method == 'POST':
        form = EquipmentTransferForm(request.POST)
        if form.is_valid():
            new_holder = form.cleaned_data['new_holder']
            are_accessories_present = form.cleaned_data['are_accessories_present']
            comment = form.cleaned_data['comment']
            change_reason = form.cleaned_data['change_reason']
            location = form.cleaned_data['location']

            history_entry = HolderHistory.objects.create(
                old_holder=equipment.holder,
                new_holder=new_holder,
                equipment=equipment,
                are_accessories_present=are_accessories_present,
                comment=comment,
                change_reason=change_reason,
                location=location,
                holding_change_date=timezone.now()
            )

            equipment.holder = new_holder
            equipment.save()

            return redirect('equipment_detail', pk=equipment_id)
        print("form not valid")
    else:
        form = EquipmentTransferForm()

    context = {
        'form_title': 'Passation de l\'équipement ' + equipment.name + "",
        'form': form,
        'equipment': equipment
    }
    return render(request, 'equipment/equipment_transfer.html', context)


@login_required
def return_to_storage(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)

    if equipment.holder != request.user:
        return redirect('equipment_list')

    storage_holder, created = Teacher.objects.get_or_create(email='storage@example.com',
                                                            defaults={'first_name': 'Storage', 'last_name': 'Room'})

    HolderHistory.objects.create(
        old_holder=equipment.holder,
        new_holder=storage_holder,
        equipment=equipment,
        are_accessories_present=True,
        comment='Retour au stockage',
        holding_change_date=timezone.now(),
        change_reason='Retour au stockage',
        location=equipment.location_room
    )

    equipment.holder = storage_holder
    equipment.save()

    return redirect('equipment_list')


def retrieve_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)

    new_holder = request.user

    if request.method == 'POST':
        form = RetrieveEquipmentForm(request.POST)
        if not form.is_valid():
            print(form.errors)
        if form.is_valid():
            equipment.holder = new_holder
            equipment.save()

            holder_history = HolderHistory(
                old_holder=storage_holder,
                new_holder=new_holder,
                equipment=equipment,
                are_accessories_present=form.cleaned_data['are_accessories_present'],
                comment=form.cleaned_data['comment'],
                holding_change_date=form.cleaned_data['holding_change_date'],
                change_reason=form.cleaned_data['change_reason'],
                location=form.cleaned_data['location']
            )
            holder_history.save()

            return redirect('equipment_list')

    else:
        form = RetrieveEquipmentForm()

    context = {'form': form, 'equipment': equipment}
    return render(request, 'equipment/equipment_retrieve.html', context)


@login_required
def history_list_view(request):
    histories = HolderHistory.objects.all().order_by('-holding_change_date')
    context = {'histories': histories}
    return render(request, 'history_list.html', context)


@login_required
def teacher_list(request):
    teachers = Teacher.objects.exclude(id=storage_holder.id)

    return render(request, 'teacher/teacher_list.html', {'teachers': teachers})


@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, 'teacher/teacher_detail.html', {'teacher': teacher})


@login_required
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                teacher = form.save()
                teacher.set_password(form.cleaned_data['password'])
                teacher.save()

                return redirect('teacher_list')
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = TeacherForm()

    return render(request, 'teacher/teacher_form.html', {'form': form, 'form_title': 'Créer un Enseignant'})


@login_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = request.POST.get('confirm_password')

            if password and password == confirm_password:
                teacher.set_password(password)

            teacher = form.save()
            teacher.save()

            return redirect('teacher_list')

    else:
        form = TeacherForm(instance=teacher)

    form_title = "Enregistrer un enseignant"
    context = {'form': form, 'form_title': form_title, 'action': 'Modifier'}

    return render(request, 'teacher/teacher_form.html', context)


@login_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'teacher/teacher_confirm_delete.html', {'teacher': teacher})


@login_required
def accessory_list(request):
    accessories = Accessory.objects.all()
    return render(request, 'accessory/accessory_list.html', {'accessories': accessories})


@login_required
def accessory_detail(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    return render(request, 'accessory/accessory_detail.html', {'accessory': accessory})


@login_required
def accessory_create(request):
    if request.method == 'POST':
        form = AccessoryForm(request.POST)
        if form.is_valid():
            accessory = form.save()
            equipment = form.cleaned_data['equipment']
            equipment.accessories.add(accessory)
            return redirect('equipment_list')
    else:
        form = AccessoryForm()

    form_title = "Enregistrer un accessoire"
    context = {'form': form, 'form_title': form_title, 'action': 'Créer'}

    return render(request, 'accessory/accessory_form.html', context)


@login_required
def accessory_update(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    if request.method == 'POST':
        form = AccessoryForm(request.POST, instance=accessory)
        if form.is_valid():
            form.save()
            return redirect('accessory_list')
    else:
        form = AccessoryForm(instance=accessory)

    form_title = "Éditer un accessoire"
    context = {'form': form, 'form_title': form_title, 'action': 'Modifier'}

    return render(request, 'accessory/accessory_form.html', context)


@login_required
def accessory_delete(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    if request.method == 'POST':
        accessory.delete()
        return redirect('accessory_list')
    return render(request, 'accessory/accessory_confirm_delete.html', {'accessory': accessory})
