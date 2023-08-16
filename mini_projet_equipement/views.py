from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Equipment
from .forms import EquipmentForm


# LOGIN

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired URL
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def equipment_list(request):
    equipments = Equipment.objects.all()
    return render(request, 'equipment/equipment_list.html', {'equipments': equipments})


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
