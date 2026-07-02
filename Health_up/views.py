from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        messages.success(request, "Registration Successful")
        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')

        messages.error(request, "Invalid Username or Password")

    return render(request, 'login.html')


def user_logout(request):
    auth_logout(request)
    return redirect('login')

@login_required 
def dashboard(request):
    return render(request, 'dashboard.html')


def prediction(request):
    result = None

    if request.method == "POST":
        age = int(request.POST.get('age', 0))
        gender = request.POST.get('gender')
        height = int(request.POST.get('height', 0))
        weight = int(request.POST.get('weight', 0))
        blood_pressure = request.POST.get('blood_pressure')
        sugar = int(request.POST.get('sugar', 0))
        heart_rate = int(request.POST.get('heart_rate', 0))

        if age > 50 or sugar > 140 or heart_rate > 100:
            result = "High Risk ⚠️"
        else:
            result = "Low Risk ✅"

    return render(request, 'prediction.html', {'result': result})