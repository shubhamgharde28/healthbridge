from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import (
    ConsultationForm,
    FollowUpForm,
    MedicalRecordForm,
    PatientForm,
    PrescriptionForm,
    SignupForm,
)
from .models import Consultation, FollowUp, MedicalRecord, Patient, Prescription


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'registration/landing.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        messages.success(request, 'Your account has been created. Please log in.')
        return redirect('login')

    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}.')
            return redirect('dashboard')
        messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required(login_url='login')
def dashboard_view(request):
    patients = Patient.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    user_patients = Patient.objects.filter(created_by=request.user)
    upcoming_consultations = Consultation.objects.filter(
        patient__created_by=request.user,
        status='scheduled',
        scheduled_at__gte=timezone.now(),
    )
    upcoming_sessions = upcoming_consultations.select_related('patient').order_by('scheduled_at')[:5]
    return render(request, 'registration/home.html', {
        'user_email': request.user.email,
        'patient_count': user_patients.count(),
        'upcoming_count': upcoming_consultations.count(),
        'record_count': MedicalRecord.objects.filter(patient__created_by=request.user).count(),
        'followup_count': FollowUp.objects.filter(patient__created_by=request.user).count(),
        'patients': patients,
        'upcoming_sessions': upcoming_sessions,
    })


@login_required(login_url='login')
def patients_view(request):
    patients = Patient.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'registration/patients.html', {'patients': patients})


@login_required(login_url='login')
def add_patient_view(request):
    form = PatientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        patient = form.save(commit=False)
        patient.created_by = request.user
        patient.save()
        messages.success(request, 'Patient registered successfully.')
        return redirect('patients')
    return render(request, 'registration/patient_form.html', {'form': form, 'title': 'Register Patient'})


@login_required(login_url='login')
def consultations_view(request):
    consultations = Consultation.objects.filter(patient__created_by=request.user).order_by('-scheduled_at')
    return render(request, 'registration/consultations.html', {'consultations': consultations})


@login_required(login_url='login')
def add_consultation_view(request):
    form = ConsultationForm(request.POST or None)
    form.fields['patient'].queryset = Patient.objects.filter(created_by=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Consultation scheduled successfully.')
        return redirect('consultations')
    return render(request, 'registration/consultation_form.html', {'form': form, 'title': 'Schedule Consultation'})


@login_required(login_url='login')
def prescriptions_view(request):
    prescriptions = Prescription.objects.filter(patient__created_by=request.user).order_by('-created_at')
    return render(request, 'registration/prescriptions.html', {'prescriptions': prescriptions})


@login_required(login_url='login')
def add_prescription_view(request):
    form = PrescriptionForm(request.POST or None, request.FILES or None)
    form.fields['patient'].queryset = Patient.objects.filter(created_by=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Prescription uploaded successfully.')
        return redirect('prescriptions')
    return render(request, 'registration/prescription_form.html', {'form': form, 'title': 'Upload Prescription'})


@login_required(login_url='login')
def followups_view(request):
    followups = FollowUp.objects.filter(patient__created_by=request.user).order_by('-follow_up_date')
    return render(request, 'registration/followups.html', {'followups': followups})


@login_required(login_url='login')
def add_followup_view(request):
    form = FollowUpForm(request.POST or None)
    form.fields['patient'].queryset = Patient.objects.filter(created_by=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Follow-up scheduled successfully.')
        return redirect('followups')
    return render(request, 'registration/followup_form.html', {'form': form, 'title': 'Schedule Follow-up'})


@login_required(login_url='login')
def medical_records_view(request):
    records = MedicalRecord.objects.filter(patient__created_by=request.user).order_by('-created_at')
    return render(request, 'registration/medical_records.html', {'records': records})


@login_required(login_url='login')
def add_medical_record_view(request):
    form = MedicalRecordForm(request.POST or None, request.FILES or None)
    form.fields['patient'].queryset = Patient.objects.filter(created_by=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Medical record saved successfully.')
        return redirect('medical_records')
    return render(request, 'registration/medical_record_form.html', {'form': form, 'title': 'Add Medical Record'})
