from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from .models import Consultation, FollowUp, MedicalRecord, Patient, Prescription


class DashboardViewTests(TestCase):
    def test_dashboard_shows_user_scoped_counts_and_future_scheduled_consultations(self):
        user = User.objects.create_user(username='care@example.com', password='test-password')
        other_user = User.objects.create_user(username='other@example.com', password='test-password')
        patient = Patient.objects.create(
            created_by=user,
            name='Asha Patel',
            age=36,
            village='Greenfield',
        )
        other_patient = Patient.objects.create(
            created_by=other_user,
            name='Other Patient',
            age=42,
            village='Elsewhere',
        )
        future_consultation = Consultation.objects.create(
            patient=patient,
            scheduled_at=timezone.now() + timedelta(days=1),
            status='scheduled',
        )
        Consultation.objects.create(
            patient=patient,
            scheduled_at=timezone.now() - timedelta(days=1),
            status='scheduled',
        )
        Consultation.objects.create(
            patient=other_patient,
            scheduled_at=timezone.now() + timedelta(days=1),
            status='scheduled',
        )
        Consultation.objects.create(
            patient=patient,
            scheduled_at=timezone.now() + timedelta(days=2),
            status='completed',
        )
        FollowUp.objects.create(
            patient=patient,
            follow_up_date=timezone.localdate() + timedelta(days=7),
        )
        MedicalRecord.objects.create(patient=patient, title='Visit summary')

        self.client.force_login(user)
        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_count'], 1)
        self.assertEqual(response.context['upcoming_count'], 1)
        self.assertEqual(response.context['followup_count'], 1)
        self.assertEqual(response.context['record_count'], 1)
        self.assertEqual(
            [consultation.pk for consultation in response.context['upcoming_sessions']],
            [future_consultation.pk],
        )
        self.assertContains(response, 'Asha Patel')
        self.assertContains(response, 'Recently added patients')


class PatientRegistrationViewTests(TestCase):
    def test_registration_form_renders_and_saves_valid_patient(self):
        user = User.objects.create_user(username='care@example.com', password='test-password')
        self.client.force_login(user)

        response = self.client.get('/patients/add/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register Patient')
        self.assertContains(response, 'Patient details')

        response = self.client.post('/patients/add/', {
            'name': 'Mina Sharma',
            'age': 29,
            'village': 'Northfield',
            'phone': '',
        })

        self.assertRedirects(response, '/patients/')
        patient = Patient.objects.get(name='Mina Sharma')
        self.assertEqual(patient.created_by, user)

    def test_registration_form_shows_field_errors(self):
        user = User.objects.create_user(username='care@example.com', password='test-password')
        self.client.force_login(user)

        response = self.client.post('/patients/add/', {
            'name': '',
            'age': 0,
            'village': '',
            'phone': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'patient-fields')


class PatientAndConsultationListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='care@example.com', password='test-password')
        self.other_user = User.objects.create_user(username='other@example.com', password='test-password')
        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Asha Patel',
            age=36,
            village='Greenfield',
            phone='555-0100',
        )
        self.other_patient = Patient.objects.create(
            created_by=self.other_user,
            name='Other Patient',
            age=42,
            village='Elsewhere',
        )
        self.client.force_login(self.user)

    def test_patient_list_shows_only_current_users_patients(self):
        response = self.client.get('/patients/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient directory')
        self.assertContains(response, 'Asha Patel')
        self.assertContains(response, 'Greenfield')
        self.assertNotContains(response, 'Other Patient')

    def test_consultation_list_shows_status_and_safe_video_link(self):
        consultation = Consultation.objects.create(
            patient=self.patient,
            scheduled_at=timezone.now() + timedelta(days=1),
            video_link='https://example.com/visit',
            status='scheduled',
        )
        Consultation.objects.create(
            patient=self.other_patient,
            scheduled_at=timezone.now() + timedelta(days=1),
            status='scheduled',
        )

        response = self.client.get('/consultations/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'All consultations')
        self.assertContains(response, 'Asha Patel')
        self.assertContains(response, 'Scheduled')
        self.assertContains(response, 'https://example.com/visit')
        self.assertContains(response, 'rel="noopener noreferrer"')
        self.assertNotContains(response, 'Other Patient')
        self.assertEqual(len(response.context['consultations']), 1)
        self.assertEqual(response.context['consultations'][0].pk, consultation.pk)


class ConsultationRegistrationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='care@example.com', password='test-password')
        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Asha Patel',
            age=36,
            village='Greenfield',
        )
        self.client.force_login(self.user)

    def test_consultation_form_renders_and_saves_valid_consultation(self):
        response = self.client.get('/consultations/add/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Schedule Consultation')
        self.assertContains(response, 'Plan the next step in care.')
        self.assertContains(response, 'Asha Patel')

        scheduled_at = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post('/consultations/add/', {
            'patient': self.patient.pk,
            'scheduled_at': scheduled_at,
            'video_link': 'https://example.com/visit',
            'notes': 'Discuss follow-up plan',
            'status': 'scheduled',
        })

        self.assertRedirects(response, '/consultations/')
        consultation = Consultation.objects.get(patient=self.patient)
        self.assertEqual(consultation.status, 'scheduled')
        self.assertEqual(consultation.video_link, 'https://example.com/visit')

    def test_consultation_form_renders_validation_errors(self):
        response = self.client.post('/consultations/add/', {
            'patient': '',
            'scheduled_at': '',
            'video_link': '',
            'notes': '',
            'status': 'scheduled',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'consultation-fields')


class PrescriptionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='care@example.com', password='test-password')
        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Asha Patel',
            age=36,
            village='Greenfield',
        )
        self.client.force_login(self.user)

    def test_prescription_list_shows_patient_document_and_empty_file_state(self):
        Prescription.objects.create(
            patient=self.patient,
            title='Medication plan',
        )

        response = self.client.get('/prescriptions/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prescription library')
        self.assertContains(response, 'Medication plan')
        self.assertContains(response, 'Asha Patel')
        self.assertContains(response, 'No file attached')

    def test_prescription_form_uploads_document_for_selected_patient(self):
        response = self.client.get('/prescriptions/add/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keep treatment details close at hand.')
        self.assertContains(response, 'enctype="multipart/form-data"')

        uploaded_file = SimpleUploadedFile('prescription.txt', b'Use as directed', content_type='text/plain')
        response = self.client.post('/prescriptions/add/', {
            'patient': self.patient.pk,
            'title': 'Medication plan',
            'description': 'Use as directed',
            'uploaded_file': uploaded_file,
        })

        self.assertRedirects(response, '/prescriptions/')
        prescription = Prescription.objects.get(patient=self.patient)
        self.assertEqual(prescription.title, 'Medication plan')
        self.assertTrue(prescription.uploaded_file.name.endswith('prescription.txt'))

    def test_prescription_form_shows_validation_errors(self):
        response = self.client.post('/prescriptions/add/', {
            'patient': '',
            'title': '',
            'description': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'prescription-fields')


class FollowUpViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='care@example.com', password='test-password')
        self.other_user = User.objects.create_user(username='other@example.com', password='test-password')
        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Asha Patel',
            age=36,
            village='Greenfield',
        )
        self.other_patient = Patient.objects.create(
            created_by=self.other_user,
            name='Other Patient',
            age=42,
            village='Elsewhere',
        )
        self.client.force_login(self.user)

    def test_followup_list_shows_only_user_records(self):
        FollowUp.objects.create(
            patient=self.patient,
            follow_up_date=timezone.localdate() + timedelta(days=7),
            notes='Check recovery',
        )
        FollowUp.objects.create(
            patient=self.other_patient,
            follow_up_date=timezone.localdate() + timedelta(days=8),
        )

        response = self.client.get('/followups/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Follow-up schedule')
        self.assertContains(response, 'Asha Patel')
        self.assertContains(response, 'Check recovery')
        self.assertNotContains(response, 'Other Patient')

    def test_followup_form_saves_valid_followup(self):
        response = self.client.get('/followups/add/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keep the next step in view.')

        follow_up_date = (timezone.localdate() + timedelta(days=7)).isoformat()
        response = self.client.post('/followups/add/', {
            'patient': self.patient.pk,
            'follow_up_date': follow_up_date,
            'notes': 'Check recovery',
        })

        self.assertRedirects(response, '/followups/')
        followup = FollowUp.objects.get(patient=self.patient)
        self.assertEqual(followup.notes, 'Check recovery')
        self.assertEqual(followup.follow_up_date.isoformat(), follow_up_date)

    def test_followup_form_renders_validation_errors(self):
        response = self.client.post('/followups/add/', {
            'patient': '',
            'follow_up_date': '',
            'notes': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'followup-fields')


class MedicalRecordViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='care@example.com', password='test-password')
        self.other_user = User.objects.create_user(username='other@example.com', password='test-password')
        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Asha Patel',
            age=36,
            village='Greenfield',
        )
        self.other_patient = Patient.objects.create(
            created_by=self.other_user,
            name='Other Patient',
            age=42,
            village='Elsewhere',
        )
        self.client.force_login(self.user)

    def test_medical_record_list_shows_only_user_records(self):
        MedicalRecord.objects.create(
            patient=self.patient,
            title='Visit summary',
            details='Recovery progressing well.',
        )
        MedicalRecord.objects.create(
            patient=self.other_patient,
            title='Other patient record',
        )

        response = self.client.get('/medical-records/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Record library')
        self.assertContains(response, 'Visit summary')
        self.assertContains(response, 'Asha Patel')
        self.assertNotContains(response, 'Other patient record')

    def test_medical_record_form_saves_record_details(self):
        response = self.client.get('/medical-records/add/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keep care history connected.')
        self.assertContains(response, 'enctype="multipart/form-data"')

        response = self.client.post('/medical-records/add/', {
            'patient': self.patient.pk,
            'title': 'Visit summary',
            'details': 'Recovery progressing well.',
        })

        self.assertRedirects(response, '/medical-records/')
        record = MedicalRecord.objects.get(patient=self.patient)
        self.assertEqual(record.title, 'Visit summary')
        self.assertEqual(record.details, 'Recovery progressing well.')

    def test_medical_record_form_renders_validation_errors(self):
        response = self.client.post('/medical-records/add/', {
            'patient': '',
            'title': '',
            'details': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'medical-record-fields')
