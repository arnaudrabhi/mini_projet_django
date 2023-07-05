from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages


# Create your views here.

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
