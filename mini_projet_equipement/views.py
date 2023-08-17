from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Subquery, OuterRef
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import Equipment, Teacher, Accessory, Purchase
from .forms import EquipmentForm, TeacherForm, AccessoryForm


class TeacherLoginView(LoginView):
    template_name = 'teacher/teacher_login.html'
    redirect_authenticated_user = True


class TeacherLogoutView(LogoutView):
    next_page = reverse_lazy('teacher_login')


def equipment_list(request):
    equipments = Equipment.objects.all()
    filter_by = request.GET.get('filter_by')
    order_by = request.GET.get('order_by')

    if filter_by:
        if filter_by == 'budget':
            equipments = equipments.annotate(
                latest_budget=Subquery(
                    Purchase.objects.filter(
                        equipment=OuterRef('pk')
                    ).order_by('-purchase_date').values('from_budget')[:1]
                )
            ).exclude(latest_budget=None).order_by('latest_budget')

        elif filter_by == 'owner':
            equipments = equipments.order_by('owner__last_name', 'owner__first_name')
        elif filter_by == 'holder':
            equipments = equipments.order_by('holder__last_name', 'holder__first_name')

    if order_by:
        equipments = equipments.order_by(order_by)

    context = {
        'equipments': equipments,
        'selected_filter': filter_by,
        'selected_order': order_by,
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
    return render(request, 'equipment/equipment_form.html', {'form': form})


def equipment_update(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'equipment/equipment_form.html', {'form': form})


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
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'teacher/teacher_form.html', {'form': form, 'action': 'Créer'})


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
