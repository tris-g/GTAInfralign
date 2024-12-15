import secrets, json
from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import AutodeskConstructionCloudProject, AutodeskConstructionCloudReport

PERMISSION_MODELS = [
    'autodeskconstructioncloudproject',
    'autodeskconstructioncloudreport',
]

PERMISSION_CODENAMES= [
    'add_autodeskconstructioncloudproject',
    'view_autodeskconstructioncloudproject',
    'change_autodeskconstructioncloudproject',
    'delete_autodeskconstructioncloudproject',
    'add_autodeskconstructioncloudreport',
    'view_autodeskconstructioncloudreport',
    'change_autodeskconstructioncloudreport',
    'delete_autodeskconstructioncloudreport',
]

SAMPLE_REPORT_DATA = json.dumps([{
    'last_updated': [{'date': 1670803200000, 'value': 1}],
    'file_sizes': [{0: 86612377}],
    'deliverables': [{'deliverable': 'D', 'value': 10}, {'deliverable': 'ND', 'value': 2}],
    'statuses': [{'status': 'A0', 'value': 3}],
    'riba_stages': [{'stage': 1, 'value': 5}],
    'versions': [{'version': 2, 'value': 1}],
}])

class TestAnalytics(TestCase):
    def setUp(self):
        self.client = Client()

        self.bad_user = User.objects.create_user(username='baduser', password=secrets.token_urlsafe(16))
        self.good_user = User.objects.create_user(username='gooduser', password=secrets.token_urlsafe(16))

        for model in PERMISSION_MODELS:
            content_type = ContentType.objects.get(app_label='analytics', model=model)
            permissions = Permission.objects.filter(content_type=content_type, codename__in=PERMISSION_CODENAMES)
            self.good_user.user_permissions.add(*permissions)
        
        self.project = AutodeskConstructionCloudProject.objects.create(
            name="Test Project",
            org="Test Organisation"
        )
        
        self.report = AutodeskConstructionCloudReport.objects.create(
            project=self.project,
            name="Test Report",
            data=SAMPLE_REPORT_DATA
        )

    def test_dashboard(self):
        self.client.force_login(self.good_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirect_to_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))
    
    def test_view_projects(self):
        self.client.force_login(self.good_user)
        response = self.client.get(reverse('view_all_projects'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects_list', response.context)
        self.assertEqual(list(response.context['projects_list']), list(AutodeskConstructionCloudProject.objects.all()))

        # Test search function
        search_response = self.client.get(reverse('view_all_projects'), {'search': 'Test'})
        self.assertEqual(search_response.status_code, 200)
        self.assertContains(search_response, self.project.name)

    def test_view_reports(self):
        self.client.force_login(self.good_user)
        response = self.client.get(reverse('view_all_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('reports_list', response.context)
        self.assertEqual(list(response.context['reports_list']), list(AutodeskConstructionCloudReport.objects.all()))

        # Test search function
        search_response = self.client.get(reverse('view_all_reports'), {'search': 'Test'})
        self.assertEqual(search_response.status_code, 200)
        self.assertContains(search_response, self.report.name)
    
    def test_add_project(self):
        self.client.force_login(self.good_user)
        response = self.client.get(reverse('add_project'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('add_project'), {'name': 'Good project', 'org': 'Good organisation'})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after success

        # Check that the book was created in the database
        self.assertEqual(AutodeskConstructionCloudProject.objects.count(), 2)  # Now two projects should exist
        self.assertTrue(AutodeskConstructionCloudProject.objects.filter(name='Good project', org='Good organisation').exists())
        
        self.client.logout()
        view_permission = Permission.objects.get(codename='view_autodeskconstructioncloudproject', content_type__app_label='analytics')
        self.bad_user.user_permissions.add(view_permission)
        self.client.force_login(self.bad_user)
        response = self.client.post(reverse('add_project'), {'name': 'Bad project', 'org': 'Bad organisation'})
        self.assertRedirects(response, reverse('view_all_projects'))
        self.bad_user.user_permissions.remove(view_permission)

    def test_add_report(self):
        self.client.force_login(self.good_user)
        response = self.client.get(reverse('add_report'))
        self.assertEqual(response.status_code, 200)

        # Load the local test Excel file
        with open('static/testing/.xlsx', 'rb') as f:
            excel_file = SimpleUploadedFile(
                ".xlsx",    # File name
                f.read(),   # File content
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # Simulate a POST request with the Excel file
        response = self.client.post(
            reverse('add_report'),  # Replace with the correct view name
            {'excel_report': excel_file, 'project': self.project.pk, 'name': 'Good report'},  # File passed in the POST data
            format='multipart'
        )

        self.assertEqual(response.status_code, 302) # Redirect on failure
        self.assertRedirects(response, reverse('view_all_reports'))
        self.assertEqual(AutodeskConstructionCloudReport.objects.count(), 2) # Now two reports should exist
        self.assertTrue(AutodeskConstructionCloudReport.objects.filter(project=self.project.pk, name='Good report').exists())
        
        self.client.logout()
        view_permission = Permission.objects.get(codename='view_autodeskconstructioncloudreport', content_type__app_label='analytics')
        self.bad_user.user_permissions.add(view_permission)
        self.client.force_login(self.bad_user)

        # Simulate a POST request with the Excel file
        response = self.client.post(
            reverse('add_report'),  # Replace with the correct view name
            {'excel_report': excel_file, 'project': self.project.pk, 'name': 'Bad report'},  # File passed in the POST data
            format='multipart'
        )

        self.assertEqual(response.status_code, 302) # Redirect on failure
        self.assertRedirects(response, reverse('view_all_reports'))
        self.assertEqual(AutodeskConstructionCloudReport.objects.count(), 2) # Still only two reports should exist
        self.assertFalse(AutodeskConstructionCloudReport.objects.filter(project=self.project.pk, name='Bad report').exists())
    
    def test_delete_project(self):
        self.client.force_login(self.good_user)
        response = self.client.post(reverse('delete_project', kwargs={'project_pk': self.project.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('view_all_projects'))
        self.assertFalse(AutodeskConstructionCloudProject.objects.filter(pk=self.project.pk).exists())

    def test_delete_report(self):
        self.client.force_login(self.good_user)
        response = self.client.post(reverse('delete_report', kwargs={'report_pk': self.report.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('view_all_reports'))
        self.assertFalse(AutodeskConstructionCloudReport.objects.filter(pk=self.report.pk).exists())