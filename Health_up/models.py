from django.db import models
from django.contrib.auth.models import User

class HealthRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    height = models.FloatField()
    weight = models.FloatField()
    bmi = models.FloatField()
    blood_pressure = models.CharField(max_length=20)
    sugar_level = models.FloatField()
    heart_rate = models.IntegerField()
    prediction = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.user.username

# Create your models here.
