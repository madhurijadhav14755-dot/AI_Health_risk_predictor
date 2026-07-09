from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('prediction/', views.prediction, name='prediction'),
    path('result/', views.result, name='result'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/', views.contact, name='contact'),

    path('medicine/', views.medicine_info, name='medicine'),
]