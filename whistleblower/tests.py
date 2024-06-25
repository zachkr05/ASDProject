from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from whistleblower.models import Report, Appeal
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Report, Appeal

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Report, Appeal

class ReportModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        # Create a test report
        cls.report = Report.objects.create(
            title='Test Report',
            description='This is a test report.',
            reported_by=cls.user,
        )

    def test_report_creation(self):
        self.assertEqual(self.report.title, 'Test Report')
        self.assertTrue(isinstance(self.report, Report))

    def test_string_representation(self):
        self.assertEqual(str(self.report), 'Test Report')

    def test_report_creation(self):
        # Test if the report instance is created successfully
        self.assertTrue(isinstance(self.report, Report))
        # Test if the report instance string representation is as expected
        self.assertEqual(self.report.__str__(), 'Test Report')


    def test_report_fields(self):
        # Retrieve the report
        report = Report.objects.get(id=self.report.id)
        # Test if the title field of the report is correct
        self.assertEqual(report.title, 'Test Report')
        # Test if the description field of the report is correct
        self.assertEqual(report.description, 'This is a test report.')
        # Test if the report is correctly associated with the user created in setUpTestData
        self.assertEqual(report.reported_by, self.user)

    def test_report_status_update(self):
        # Update the status of the report
        self.report.status = 'in_progress'
        self.report.save()
        # Retrieve the updated report
        updated_report = Report.objects.get(id=self.report.id)
        # Test if the status field of the report has been updated correctly
        self.assertEqual(updated_report.status, 'in_progress', "Report status should be updated to 'in_progress'.")

    def test_report_anonymity_feature(self):
        # Mark the report to appear anonymous
        self.report.appear_anonymous = True
        self.report.save()
        # Retrieve the updated report
        updated_report = Report.objects.get(id=self.report.id)
        # Test if the report is marked to appear anonymoutestusers
        self.assertTrue(updated_report.appear_anonymous, "Report should be marked to appear anonymous.")

    def test_report_publication_status_management(self):
        # Set the publication status of the report to 'Published'
        self.report.publication_status = 'Published'
        self.report.save()
        # Retrieve the updated report
        updated_report = Report.objects.get(id=self.report.id)
        # Test if the publication status of the report has been set to 'Published'
        self.assertEqual(updated_report.publication_status, 'Published', "Report publication status should be 'Published'.")

    def test_user_pending_submissions_unauthenticated_access(self):
        response = self.client.get(reverse('whistleblower:pending_submissions'))
        self.assertIn(reverse('accounts:signin'), response.url)
    
    def test_upvote_report(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('whistleblower:upvote_report', args=[self.report.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.report.upvotes.count(), 1)
    
    def test_downvote_report(self):
        self.client.login(username='testuser', password='testpass')
        self.report.upvotes.add(self.user)
        response = self.client.post(reverse('whistleblower:downvote_report', args=[self.report.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.report.downvotes.count(), 1)


        
    





