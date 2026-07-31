from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import HealthRecord
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime
import joblib
from django.shortcuts import render
from django.conf import settings
import requests




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


        messages.success(
            request,
            "Registration Successful!"
        )

        return redirect("login")


    return render(request, "register.html")



# ==========================
# LOGIN
# ==========================
def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")


        user = authenticate(
            request,
            username=username,
            password=password
        )


        if user is not None:

            login(request, user)

            return redirect("prediction")


        else:

            messages.error(
                request,
                "Invalid Username or Password"
            )


    return render(request, "login.html")



# ==========================
# LOGOUT
# ==========================
def user_logout(request):

    logout(request)

    return redirect("home")

# ==========================
# RESULT
# ==========================

@login_required
def result(request):

    

    context = {
    "age": request.session.get("age"),
    "gender": request.session.get("gender"),
    "date": request.session.get("date"),
    "bmi": request.session.get("bmi"),
    "bmi_category": request.session.get("bmi_category"),
    "disease": request.session.get("disease"),
    "risk": request.session.get("risk"),
    "confidence": request.session.get("confidence"),
    "recommendation": request.session.get("recommendation"),
    "analysis": request.session.get("analysis"),
    "tip": request.session.get("tip"),
    "tests": request.session.get("tests", []),
    "symptoms": request.session.get("symptoms", []),
}

    return render(request, "result.html", context)

        

    

model = joblib.load("ml_model/model.pkl")


@login_required
def prediction(request):

    if request.method == "POST":

        # ==========================
        # Get Form Data
        # ==========================

        age = int(request.POST.get("age"))
        gender = request.POST.get("gender")

        height = float(request.POST.get("height"))
        weight = float(request.POST.get("weight"))

        symptoms = request.POST.getlist("symptoms")

        # ==========================
        # Validation
        # ==========================

        if not (1 <= age <= 120):
            messages.error(request, "Invalid Age")
            return redirect("prediction")

        if not (50 <= height <= 250):
            messages.error(request, "Invalid Height")
            return redirect("prediction")

        if not (10 <= weight <= 300):
            messages.error(request, "Invalid Weight")
            return redirect("prediction")

        # ==========================
        # BMI Calculation
        # ==========================

        bmi = round(weight / ((height / 100) ** 2), 1)

        if bmi < 18.5:
            bmi_category = "Underweight"

        elif bmi < 25:
            bmi_category = "Normal"

        elif bmi < 30:
            bmi_category = "Overweight"

        else:
            bmi_category = "Obese"

        # ==========================
        # Initial Scores
        # ==========================

        diabetes = 0
        bp = 0
        heart = 0

        # ==========================
        # Symptom Based Scoring
        # ==========================

        if "Excessive Thirst" in symptoms:
            diabetes += 20

        if "Frequent Urination" in symptoms:
            diabetes += 20

        if "Blurred Vision" in symptoms:
            diabetes += 15

        if "Fatigue" in symptoms:
            diabetes += 10
            heart += 10

        if "Headache" in symptoms:
            bp += 15

        if "Dizziness" in symptoms:
            bp += 15

        if "Chest Pain" in symptoms:
            heart += 25

        if "Shortness of Breath" in symptoms:
            heart += 20

        if "Irregular Heartbeat" in symptoms:
            heart += 20

        if "Nausea" in symptoms:
            diabetes += 5

        if "Fever" in symptoms:
            diabetes += 5

        if "Cough" in symptoms:
            heart += 5

        # ==========================
        # Final Disease Prediction
        # ==========================

        if diabetes >= bp and diabetes >= heart:

            disease = "Possible Diabetes Risk"
            confidence = diabetes

            recommendation = (
                "Reduce sugar intake, exercise regularly "
                "and consult a physician."
            )

            tests = [
                "Blood Sugar Test",
                "HbA1c Test"
            ]

        elif bp >= diabetes and bp >= heart:

            disease = "Possible Blood Pressure Risk"
            confidence = bp

            recommendation = (
                "Reduce salt intake, avoid stress "
                "and monitor blood pressure."
            )

            tests = [
                "Blood Pressure Check",
                "Kidney Function Test"
            ]

        else:

            disease = "Possible Heart Disease Risk"
            confidence = heart

            recommendation = (
                "Maintain a heart healthy lifestyle "
                "and consult a cardiologist."
            )

            tests = [
                "ECG",
                "2D Echo"
            ]

        # ==========================
        # Health Score
        # ==========================

        health_score = 100 - confidence

        if health_score < 0:
            health_score = 0

        if health_score >= 80:
            health_status = "Excellent"

        elif health_score >= 60:
            health_status = "Good"

        elif health_score >= 40:
            health_status = "Average"

        else:
            health_status = "Poor"

        # ==========================
        # Water Intake
        # ==========================

        water_intake = round(weight * 35 / 1000, 1)

        if water_intake < 2:
            water_status = "Drink More Water"

        elif water_intake <= 3:
            water_status = "Good Hydration"

        else:
            water_status = "Excellent Hydration"

        # ==========================
        # Ideal Weight
        # ==========================

        height_m = height / 100

        ideal_weight_min = round(18.5 * (height_m ** 2), 1)
        ideal_weight_max = round(24.9 * (height_m ** 2), 1)

        if weight < ideal_weight_min:
            weight_status = "Underweight"

        elif weight > ideal_weight_max:
            weight_status = "Overweight"

        else:
            weight_status = "Healthy Weight"

        # ==========================
        # Food Recommendation
        # ==========================

        if "Diabetes" in disease:

            foods_to_eat = [
                "🥬 Green Vegetables",
                "🍎 Apple",
                "🥣 Oats",
                "🐟 Fish",
                "🥜 Almonds"
            ]

            foods_to_avoid = [
                "🍬 Sugar",
                "🥤 Soft Drinks",
                "🍰 Cake",
                "🍟 Fast Food",
                "🍫 Chocolate"
            ]

            exercises = [
                "🚶 Walking (30 Minutes)",
                "🚴 Cycling",
                "🧘 Yoga",
                "🏃 Light Jogging"
            ]

        elif "Blood Pressure" in disease:

            foods_to_eat = [
                "🍌 Banana",
                "🥬 Spinach",
                "🥛 Low Fat Milk",
                "🍅 Tomato"
            ]

            foods_to_avoid = [
                "🧂 Salt",
                "🍔 Burger",
                "🍕 Pizza",
                "🍟 Chips"
            ]

            exercises = [
                "🚶 Morning Walk",
                "🧘 Meditation",
                "🌬 Breathing Exercise",
                "🤸 Stretching"
            ]

        else:

            foods_to_eat = [
                "🐟 Fish",
                "🥦 Broccoli",
                "🥜 Walnuts",
                "🥑 Avocado"
            ]

            foods_to_avoid = [
                "🍗 Fried Food",
                "🥓 Bacon",
                "🍔 Burger",
                "🍟 French Fries"
            ]

            exercises = [
                "🚶 Slow Walking",
                "🧘 Yoga",
                "🌬 Deep Breathing",
                "🤸 Stretching"
            ]

        # ==========================
        # Overall Risk
        # ==========================

        if confidence >= 70:
            risk = "High"

        elif confidence >= 40:
            risk = "Medium"

        else:
            risk = "Low"


                # Sugar Status
        if diabetes >= 70:
            sugar_status = "High Risk"
        elif diabetes >= 40:
            sugar_status = "Medium Risk"
        else:
            sugar_status = "Normal"

        # Blood Pressure Status
        if bp >= 70:
            bp_status = "High Risk"
        elif bp >= 40:
            bp_status = "Medium Risk"
        else:
            bp_status = "Normal"

        # Heart Status
        if heart >= 70:
            heart_status = "High Risk"
        elif heart >= 40:
            heart_status = "Medium Risk"
        else:
            heart_status = "Normal"
        # ==========================
        # AI Analysis
        # ==========================

        analysis = (
            f"Based on the selected symptoms, your health risk is {risk}. "
            f"The predicted condition is {disease}. "
            f"Health Score: {health_score}/100."
        )

        tip = (
            "⚠ This AI prediction is for educational purposes only. "
            "Please consult a qualified doctor for medical advice."
        )

        HealthRecord.objects.create(
            user=request.user,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            bmi=bmi,
            bmi_category=bmi_category,
            symptoms=", ".join(symptoms),
            disease=disease,
            risk=risk,
            confidence=confidence,
            sugar_status=sugar_status,
            bp_status=bp_status,
            heart_status=heart_status,
            recommendation=recommendation,
            tip=tip,
            blood_pressure=bp_status,
            sugar_level=diabetes,
            heart_rate=heart,
            water=water_intake,
        )

        return render(request, "result.html", {
            "disease": disease,
            "risk": risk,
            "confidence": confidence,
            "age": age,
            "gender": gender,
            "date": datetime.now().strftime("%d/%m/%Y"),
            "bmi": bmi,
            "bmi_category": bmi_category,
            "sugar_status": sugar_status,
            "bp_status": bp_status,
            "heart_status": heart_status,
            "health_score": health_score,
            "health_status": health_status,
            "water_intake": water_intake,
            "water_status": water_status,
            "ideal_weight_min": ideal_weight_min,
            "ideal_weight_max": ideal_weight_max,
            "weight_status": weight_status,
            "foods_to_eat": foods_to_eat,
            "foods_to_avoid": foods_to_avoid,
            "exercises": exercises,
            "symptoms": symptoms,
            "analysis": analysis,
            "recommendation": recommendation,
            "tests": tests,
            "tip": tip,
        })

    return render(request, "prediction.html")
#=========================
# Dashboard 
#==========================
@login_required
def dashboard(request):

    records = HealthRecord.objects.filter(
        user=request.user
    ).order_by("-created_at")

    total_predictions = records.count()

    low_risk = records.filter(risk="Low").count()
    medium_risk = records.filter(risk="Medium").count()
    high_risk = records.filter(risk="High").count()

    current_prediction = records.first()
    last_prediction = records.first()

    previous_predictions = records

    context = {
        "records": records,
        "total_predictions": total_predictions,
        "low_risk": low_risk,
        "medium_risk": medium_risk,
        "high_risk": high_risk,
        "current_prediction": current_prediction,
        "last_prediction": last_prediction,
        "previous_predictions": previous_predictions,
    }

    return render(request, "dashboard.html", context)
# ==========================
# CONTACT
# ==========================

def contact(request):

    if request.method == "POST":

        messages.success(
            request,
            "Message sent successfully!"
        )

        return redirect("contact")


    return render(
        request,
        "contact.html"
    )



# ==========================
# OPENFDA + USDA INFORMATION
# ==========================

def medicine_info(request):

    data = None
    food = None


    if request.method == "POST":


        # ======================
        # MEDICINE SEARCH (OPENFDA)
        # ======================

        medicine_name = request.POST.get(
            "medicine",
            ""
        ).strip()


        if medicine_name:


            medicine_map = {

                "dolo": "acetaminophen",
                "dolo 650": "acetaminophen",
                "crocin": "acetaminophen",
                "paracetamol": "acetaminophen",

                "calpol": "acetaminophen",
                "tylenol": "acetaminophen",

                "azithral": "azithromycin",
                "azithro": "azithromycin",
                "azithromycin": "azithromycin",

                "augmentin": "amoxicillin",
                "amoxicillin": "amoxicillin",

                "combiflam": "ibuprofen",
                "brufen": "ibuprofen",
                "ibuprofen": "ibuprofen",

                "pantop": "pantoprazole",
                "pantoprazole": "pantoprazole",

                "omee": "omeprazole",
                "omeprazole": "omeprazole",

                "glycomet": "metformin",
                "metformin": "metformin",

                "atorva": "atorvastatin",
                "atorvastatin": "atorvastatin",

                "disprin": "aspirin",
                "aspirin": "aspirin"
            }


            search_name = medicine_map.get(
                medicine_name.lower(),
                medicine_name
            )


            url = "https://api.fda.gov/drug/label.json"


            params = {

                "api_key": settings.OPENFDA_API_KEY,

                "search":
                (
                    f'openfda.generic_name:"{search_name}" '
                    f'OR openfda.brand_name:"{search_name}" '
                    f'OR openfda.substance_name:"{search_name}"'
                ),

                "limit": 10
            }


            try:

                response = requests.get(
                    url,
                    params=params,
                    timeout=10
                )


                print("FDA URL:", response.url)
                print("STATUS:", response.status_code)


                results = response.json().get(
                    "results",
                    []
                )


                medicine = None


                for item in results:


                    openfda = item.get(
                        "openfda",
                        {}
                    )


                    names = (
                        openfda.get(
                            "brand_name",
                            []
                        )
                        +
                        openfda.get(
                            "generic_name",
                            []
                        )
                    )


                    for name in names:


                        if search_name.lower() in name.lower():

                            medicine = item
                            break


                    if medicine:
                        break



                if medicine:


                    data = {

                        "name": openfda.get(
                            "brand_name",
                            ["Not Available"]
                        )[0],


                        "generic_name": openfda.get(
                            "generic_name",
                            ["Not Available"]
                        )[0],


                        "category": openfda.get(
                            "pharm_class_epc",
                            ["Not Available"]
                        )[0],


                        "purpose": " ".join(
                            medicine.get(
                                "purpose"
                            )
                            or
                            medicine.get(
                                "indications_and_usage"
                            )
                            or
                            ["Not Available"]
                        ),


                        "dosage": " ".join(
                            medicine.get(
                                "dosage_and_administration"
                            )
                            or
                            ["Not Available"]
                        ),


                        "side_effects": " ".join(
                            medicine.get(
                                "adverse_reactions"
                            )
                            or
                            ["Not Available"]
                        ),


                        "precautions": " ".join(
                            medicine.get(
                                "warnings"
                            )
                            or
                            ["Not Available"]
                        )

                    }


                else:

                    data = {
                        "error": "Medicine not found."
                    }



            except requests.exceptions.RequestException:


                data = {
                    "error": "OpenFDA connection error."
                }



        # ======================
        # FOOD SEARCH (USDA)
        # ======================
        food_name = request.POST.get(
            "food_name",
            ""
        ).strip()


        if food_name:

            url = "https://api.nal.usda.gov/fdc/v1/foods/search"

            params = {
                "api_key": settings.USDA_API_KEY,
                "query": food_name,
                "pageSize": 1
            }

            try:

                response = requests.get(
                    url,
                    params=params,
                    timeout=10
                )

                result = response.json()

                if result.get("foods"):

                    food_data = result["foods"][0]

                    food = {
                        "name": food_data.get("description", "Not Available"),
                        "calories": "Not Available",
                        "protein": "Not Available",
                        "nutrients": []
                    }

                    for nutrient in food_data.get("foodNutrients", []):

                        nutrient_name = nutrient.get("nutrientName")
                        value = nutrient.get("value")
                        unit = nutrient.get("unitName")

                        food["nutrients"].append({
                            "name": nutrient_name,
                            "value": value,
                            "unit": unit
                        })

                        if nutrient_name == "Energy":
                            food["calories"] = str(value) + " " + unit

                        if nutrient_name == "Protein":
                            food["protein"] = str(value) + " " + unit

            except requests.exceptions.RequestException:

                food = None


    return render(
        request,
        "medicine.html",
        {
            "data": data,
            "food": food
        }
    )
# ==========================
# DOWNLOAD PDF REPORT
# ==========================

@login_required
def download_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="Health_Report.pdf"'
    )


    p = canvas.Canvas(response)



    # Title

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawString(
        180,
        800,
        "AI Health Report"
    )



    p.setFont(
        "Helvetica",
        12
    )



    # Patient Report

    y = 760


    report_data = [

    f"Possible Disease : {request.session.get('disease')}",

    f"Risk Level : {request.session.get('risk')}",

    f"Confidence : {request.session.get('confidence')}%",

    f"Age : {request.session.get('age')}",

    f"Gender : {request.session.get('gender')}",

    f"BMI : {request.session.get('bmi')} ({request.session.get('bmi_category')})",

    f"AI Analysis : {request.session.get('analysis')}",

    f"Recommendation : {request.session.get('recommendation')}",

    f"Disclaimer : {request.session.get('tip')}"
]



    for line in report_data:

        p.drawString(
            50,
            y,
            line
        )

        y -= 20



    p.save()


    return response

