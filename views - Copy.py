from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import HealthRecord


# ==========================
# HOME
# ==========================
def home(request):
    return render(request, "home.html")


# ==========================
# ABOUT
# ==========================
def about(request):
    return render(request, "about.html")


# ==========================
# REGISTER
# ==========================
def register(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        messages.success(request, "Registration Successful!")
        return redirect("login")

    return render(request, "register.html")


# ==========================
# LOGIN
# ==========================
def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("prediction")

        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "login.html")


# ==========================
# LOGOUT
# ==========================
def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def result(request):

    context = {
        "risk": request.session.get("risk"),
        "score": request.session.get("score"),
        "bmi": request.session.get("bmi"),
        "status": request.session.get("status"),
        "recommendation": request.session.get("recommendation"),
    }

    return render(request, "result.html", context)
# ==========================
# PREDICTION
# ==========================
@login_required
def prediction(request):

    if request.method == "POST":
        print("POST received")

        age = int(request.POST.get("age"))
        height = float(request.POST.get("height"))
        weight = float(request.POST.get("weight"))
        sugar = float(request.POST.get("sugar_level"))
        heart = int(request.POST.get("heart_rate"))
        bp = request.POST.get("blood_pressure")
        gender = request.POST.get("gender")

        bmi = round(weight / ((height / 100) ** 2), 2)

        score = 0

        if bmi >= 30:
            score += 35
        elif bmi >= 25:
            score += 20

        if sugar > 140:
            score += 25

        if heart > 100:
            score += 20

        if bp == "High":
            score += 20

        if age >= 60:
            score += 20

        if score < 30:
            risk = "Low"
            status = "Healthy"
            recommendation = "Maintain your healthy lifestyle."

        elif score < 60:
            risk = "Medium"
            status = "Average"
            recommendation = "Exercise regularly and eat a balanced diet."

        else:
            risk = "High"
            status = "Unhealthy"
            recommendation = "Consult a doctor immediately."

        HealthRecord.objects.create(
            user=request.user,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            bmi=bmi,
            blood_pressure=bp,
            sugar_level=sugar,
            heart_rate=heart,
            prediction=risk
        )

        request.session["risk"] = risk
        request.session["score"] = score
        request.session["bmi"] = bmi
        request.session["status"] = status
        request.session["recommendation"] = recommendation
        
    
        return redirect("result")
    

    return render(request, "prediction.html")


# ==========================
# DASHBOARD
# ==========================
@login_required
def dashboard(request):

    records = HealthRecord.objects.filter(user=request.user).order_by("-id")

    context = {
        "records": records
    }

    return render(request, "dashboard.html", context)


# ==========================
# CONTACT
# ==========================
def contact(request):

    if request.method == "POST":
        messages.success(request, "Message sent successfully!")
        return redirect("contact")

    return render(request, "contact.html")


import requests

def medicine_info(request):

    data = None

    if request.method == "POST":
        medicine_name = request.POST.get("medicine")

        url = "https://api.fda.gov/drug/label.json"

        params = {
            "search": f"openfda.brand_name:{medicine_name}",
            "limit": 1
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            result = response.json()

            try:
                medicine = result["results"][0]

                data = {
                    "name": medicine.get("openfda", {}).get("brand_name", ["Not Found"])[0],
                    "purpose": medicine.get("purpose", ["Not Available"])[0],
                    "warning": medicine.get("warnings", ["Not Available"])[0]
                }

            except:
                data = {"error": "Medicine not found"}

    return render(request, "medicine.html", {"data": data})