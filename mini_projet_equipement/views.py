from django.contrib.auth.views import LoginView, LogoutView
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Equipment, Teacher, Accessory
from .forms import EquipmentForm, TeacherForm, AccessoryForm
from django.shortcuts import render

class TeacherLoginView(LoginView):
    template_name = 'teacher/teacher_login.html'
    redirect_authenticated_user = True


class TeacherLogoutView(LogoutView):
    next_page = reverse_lazy('teacher_login')


def equipment_list(request):
    filter_by = request.GET.get('filter_by')
    filter_value = request.GET.get('filter_value')
    order_by = request.GET.get('order_by')

    equipments = Equipment.objects.all()
    filter_values = []

    if filter_by == 'budget':
        # Add budget options here based on your data
        pass
    elif filter_by == 'holder':
        filter_values = list(set(equipments.values_list('holder__first_name', flat=True)))
    elif filter_by == 'owner':
        filter_values = list(set(equipments.values_list('owner__first_name', flat=True)))

    if filter_by == 'budget':
        equipments = equipments.annotate(latest_budget=models.Max('purchases__from_budget'))
    elif filter_by == 'holder':
        equipments = equipments.filter(holder__first_name=filter_value)
    elif filter_by == 'owner':
        equipments = equipments.filter(owner__first_name=filter_value)

    if order_by:
        equipments = equipments.order_by(order_by)

    context = {
        'equipments': equipments,
        'selected_filter': filter_by,
        'selected_value': filter_value,
        'selected_order': order_by,
        'filter_values': filter_values,
    }

    return render(request, 'equipment/equipment_list.html', context)


def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    return render(request, 'equipment/equipment_detail.html', {'equipment': equipment})


def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm()

    form_title = "Enregistrer un nouvel équipement"  # Set the form title
    context = {'form': form, 'form_title': form_title}
    return render(request, 'equipment/equipment_form.html', context)


def equipment_update(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm(instance=equipment)

    form_title = "Éditer un équipement"  # Set the form title
    context = {'form': form, 'form_title': form_title}

    return render(request, 'equipment/equipment_form.html', context)


def equipment_delete(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        equipment.delete()
        return redirect('equipment_list')
    return render(request, 'equipment/equipment_confirm_delete.html', {'equipment': equipment})


def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'teacher/teacher_list.html', {'teachers': teachers})


def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, 'teacher/teacher_detail.html', {'teacher': teacher})


def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                teacher = form.save()
                # ... (other logic)
                return redirect('teacher_list')
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = TeacherForm()

    return render(request, 'teacher/teacher_form.html', {'form': form, 'form_title': 'Créer un Enseignant'})


def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'teacher/teacher_form.html', {'form': form, 'action': 'Modifier'})


def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'teacher/teacher_confirm_delete.html', {'teacher': teacher})


def accessory_list(request):
    accessories = Accessory.objects.all()
    return render(request, 'accessory/accessory_list.html', {'accessories': accessories})


def accessory_detail(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    return render(request, 'accessory/accessory_detail.html', {'accessory': accessory})


def accessory_create(request):
    if request.method == 'POST':
        form = AccessoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accessory_list')
    else:
        form = AccessoryForm()
    return render(request, 'accessory/accessory_form.html', {'form': form, 'action': 'Créer'})


def accessory_update(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    if request.method == 'POST':
        form = AccessoryForm(request.POST, instance=accessory)
        if form.is_valid():
            form.save()
            return redirect('accessory_list')
    else:
        form = AccessoryForm(instance=accessory)
    return render(request, 'accessory/accessory_form.html', {'form': form, 'action': 'Modifier'})


def accessory_delete(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    if request.method == 'POST':
        accessory.delete()
        return redirect('accessory_list')
    return render(request, 'accessory/accessory_confirm_delete.html', {'accessory': accessory})
