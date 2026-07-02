from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('patients/', views.patients_view, name='patients'),
    path('patients/add/', views.add_patient_view, name='add_patient'),
    path('consultations/', views.consultations_view, name='consultations'),
    path('consultations/add/', views.add_consultation_view, name='add_consultation'),
    path('prescriptions/', views.prescriptions_view, name='prescriptions'),
    path('prescriptions/add/', views.add_prescription_view, name='add_prescription'),
    path('followups/', views.followups_view, name='followups'),
    path('followups/add/', views.add_followup_view, name='add_followup'),
    path('medical-records/', views.medical_records_view, name='medical_records'),
    path('medical-records/add/', views.add_medical_record_view, name='add_medical_record'),
]
