from django.db import models
from django.contrib.auth.models import User


class HealthRecord(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )


    # ==========================
    # Basic Information
    # ==========================

    age = models.IntegerField()

    gender = models.CharField(
        max_length=10
    )

    height = models.FloatField()

    weight = models.FloatField()

    bmi = models.FloatField()


    bmi_category = models.CharField(
        max_length=50,
        default="Not Available"
    )



    # ==========================
    # Health Parameters
    # ==========================

    blood_pressure = models.CharField(
        max_length=20,
        default="Not Available"
    )


    sugar_level = models.FloatField(
        default=0
    )


    heart_rate = models.IntegerField(
        default=0
    )



    # ==========================
    # Symptoms
    # ==========================

    symptoms = models.TextField(
        default=""
    )



    # ==========================
    # Lifestyle Information
    # ==========================

    smoking = models.CharField(
        max_length=20,
        default="No"
    )


    alcohol = models.CharField(
        max_length=20,
        default="No"
    )


    stress = models.CharField(
        max_length=20,
        default="Low"
    )


    exercise = models.CharField(
        max_length=50,
        default="Regular"
    )


    sleep = models.FloatField(
        default=0
    )


    water = models.FloatField(
        default=0
    )



    # ==========================
    # AI Prediction Result
    # ==========================

    disease = models.CharField(
        max_length=100,
        default="Unknown"
    )


    risk = models.CharField(
        max_length=20,
        default="Low"
    )


    confidence = models.FloatField(
        default=0
    )



    # Individual Health Analysis

    sugar_status = models.CharField(
        max_length=50,
        default="Normal"
    )


    bp_status = models.CharField(
        max_length=50,
        default="Normal"
    )


    heart_status = models.CharField(
        max_length=50,
        default="Normal"
    )



    recommendation = models.TextField(
        default=""
    )


    tip = models.TextField(
        default=""
    )



    # ==========================
    # Date
    # ==========================

    created_at = models.DateTimeField(
        auto_now_add=True
    )



    def __str__(self):

        return f"{self.user.username} - {self.disease}"