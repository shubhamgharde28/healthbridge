from django.contrib import admin

from .models import Consultation, FollowUp, MedicalRecord, Patient, Prescription


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'village', 'phone', 'created_by', 'created_at')
    search_fields = ('name', 'village', 'phone')


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'scheduled_at', 'status', 'video_link', 'created_at')
    list_filter = ('status',)
    search_fields = ('patient__name', 'video_link')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'created_at')
    search_fields = ('title', 'patient__name')


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('patient', 'follow_up_date', 'created_at')
    search_fields = ('patient__name',)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'created_at')
    search_fields = ('title', 'patient__name')
