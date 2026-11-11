from datetime import timedelta
from django.core.exceptions import ValidationError, PermissionDenied
from django.test import TestCase
from django.utils import timezone

from accounts.models import RegisteredUser, Role
from .models import Report, ReportCategory, ReportStatus
from .services import ReportService


class ReportDomainAndServiceTests(TestCase):
    def setUp(self):
        self.user = RegisteredUser.objects.create_user(
            email='reporter@campus.edu',
            password='password123',
            full_name='Campus Reporter',
            role=Role.REGISTERED
        )
        self.valid_lat = 23.759791
        self.valid_lng = 90.348268

    def test_validate_boundary_inside(self):
        self.assertTrue(ReportService.validate_boundary(self.valid_lat, self.valid_lng))

    def test_validate_boundary_outside(self):
        outside_lat = 23.850000
        outside_lng = 90.500000
        with self.assertRaises(ValidationError) as ctx:
            ReportService.validate_boundary(outside_lat, outside_lng)
        self.assertIn('Outside campus boundary', str(ctx.exception))

    def test_validate_boundary_outside_polygon_geometry(self):
        # Point within bounding box but outside the irregular polygon perimeter
        corner_lat = 23.758200
        corner_lng = 90.347400
        with self.assertRaises(ValidationError) as ctx:
            ReportService.validate_boundary(corner_lat, corner_lng)
        self.assertIn('Outside campus boundary', str(ctx.exception))

    def test_check_rate_limit_enforced_at_eight(self):
        # 7 reports allowed
        for i in range(7):
            Report.objects.create(
                user=self.user,
                latitude=self.valid_lat,
                longitude=self.valid_lng,
                category=ReportCategory.STAGNANT_WATER
            )
        self.assertTrue(ReportService.check_rate_limit(self.user))

        # 8th report
        Report.objects.create(
            user=self.user,
            latitude=self.valid_lat,
            longitude=self.valid_lng,
            category=ReportCategory.MANY_MOSQUITOES
        )

        # 9th attempt raises "Too many reports today"
        with self.assertRaises(ValidationError) as ctx:
            ReportService.check_rate_limit(self.user)
        self.assertIn('Too many reports today', str(ctx.exception))

    def test_past_day_reports_do_not_count_towards_today(self):
        # Create reports marked as yesterday
        yesterday = timezone.now() - timedelta(days=1)
        r = Report.objects.create(
            user=self.user,
            latitude=self.valid_lat,
            longitude=self.valid_lng,
            category=ReportCategory.BITE_INCIDENT
        )
        Report.objects.filter(id=r.id).update(created_at=yesterday)

        # Today should still allow 8 reports
        self.assertTrue(ReportService.check_rate_limit(self.user))

    def test_create_report_success(self):
        data = {
            'latitude': self.valid_lat,
            'longitude': self.valid_lng,
            'category': ReportCategory.STAGNANT_WATER,
            'note': 'Near cafeteria flowerpots'
        }
        report = ReportService.create_report(self.user, data)
        self.assertIsNotNone(report.id)
        self.assertEqual(report.status, ReportStatus.VISIBLE)
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.note, 'Near cafeteria flowerpots')

    def test_create_report_outside_boundary_fails(self):
        data = {
            'latitude': 23.850000,
            'longitude': 90.500000,
            'category': ReportCategory.STAGNANT_WATER
        }
        with self.assertRaises(ValidationError) as ctx:
            ReportService.create_report(self.user, data)
        self.assertIn('Outside campus boundary', str(ctx.exception))
        self.assertEqual(Report.objects.count(), 0)

    def test_create_report_unauthenticated_fails(self):
        data = {
            'latitude': self.valid_lat,
            'longitude': self.valid_lng,
            'category': ReportCategory.STAGNANT_WATER
        }
        with self.assertRaises(PermissionDenied):
            ReportService.create_report(None, data)

    def test_active_queryset_filters_hidden_and_resolved(self):
        r1 = Report.objects.create(
            user=self.user,
            latitude=self.valid_lat,
            longitude=self.valid_lng,
            category=ReportCategory.STAGNANT_WATER,
            status=ReportStatus.VISIBLE
        )
        r2 = Report.objects.create(
            user=self.user,
            latitude=self.valid_lat,
            longitude=self.valid_lng,
            category=ReportCategory.MANY_MOSQUITOES,
            status=ReportStatus.HIDDEN
        )
        r3 = Report.objects.create(
            user=self.user,
            latitude=self.valid_lat,
            longitude=self.valid_lng,
            category=ReportCategory.BITE_INCIDENT,
            status=ReportStatus.RESOLVED
        )

        active = list(Report.objects.active())
        self.assertIn(r1, active)
        self.assertNotIn(r2, active)
        self.assertNotIn(r3, active)

    def test_model_methods_hide_and_mark_resolved(self):
        report = Report.objects.create(
            user=self.user,
            latitude=self.valid_lat,
            longitude=self.valid_lng,
            category=ReportCategory.STAGNANT_WATER
        )
        self.assertEqual(report.status, ReportStatus.VISIBLE)

        report.hide()
        report.refresh_from_db()
        self.assertEqual(report.status, ReportStatus.HIDDEN)

        report.mark_resolved('Drain cleared and sprayed')
        report.refresh_from_db()
        self.assertEqual(report.status, ReportStatus.RESOLVED)
        self.assertEqual(report.resolved_note, 'Drain cleared and sprayed')

    def test_create_report_none_note_def_07(self):
        data = {
            'latitude': self.valid_lat,
            'longitude': self.valid_lng,
            'category': ReportCategory.STAGNANT_WATER,
            'note': None
        }
        report = ReportService.create_report(self.user, data)
        self.assertEqual(report.note, '')

    def test_create_report_photo_in_data_def_10(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        photo = SimpleUploadedFile('test.jpg', b'dummy_content', content_type='image/jpeg')
        data = {
            'latitude': self.valid_lat,
            'longitude': self.valid_lng,
            'category': ReportCategory.STAGNANT_WATER,
            'note': 'Photo test',
            'photo': photo
        }
        report = ReportService.create_report(self.user, data)
        self.assertIsNotNone(report.photo)
        if report.photo:
            report.photo.delete(save=False)


class ReportViewIntegrationTests(TestCase):
    def setUp(self):
        self.user = RegisteredUser.objects.create_user(
            email='student_view@campus.edu',
            password='password123',
            full_name='Test Student'
        )

    def test_heatmap_public_access(self):
        # Unauthenticated guest can view heatmap
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campus Risk Heatmap')
        self.assertContains(response, 'Sign In Required')
        self.assertContains(response, 'report-gate-modal')

    def test_report_create_view_requires_login(self):
        # Guest is redirected to login
        response = self.client.get('/report/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/accounts/login/' in response.url or 'login' in response.url)

    def test_report_create_view_logged_in_access(self):
        self.client.login(username='student_view@campus.edu', password='password123')
        response = self.client.get('/report/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Report Mosquito Activity')

    def test_report_create_post_success(self):
        self.client.login(username='student_view@campus.edu', password='password123')
        post_data = {
            'latitude': 23.759791,
            'longitude': 90.348268,
            'category': ReportCategory.MANY_MOSQUITOES,
            'note': 'Library back garden'
        }
        response = self.client.post('/report/', post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Report submitted successfully.')
        self.assertEqual(Report.objects.count(), 1)

    def test_report_create_post_outside_boundary(self):
        self.client.login(username='student_view@campus.edu', password='password123')
        post_data = {
            'latitude': 23.850000,
            'longitude': 90.500000,
            'category': ReportCategory.MANY_MOSQUITOES,
            'note': 'Off campus'
        }
        response = self.client.post('/report/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Outside campus boundary')
        self.assertEqual(Report.objects.count(), 0)

    def test_heatmap_popup_datetime_local_def_08(self):
        report = Report.objects.create(
            user=self.user,
            latitude=23.759791,
            longitude=90.348268,
            category=ReportCategory.STAGNANT_WATER,
            status=ReportStatus.VISIBLE
        )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        reports_data = response.context['reports_data']
        self.assertEqual(len(reports_data), 1)
        expected_str = timezone.localtime(report.created_at).strftime('%b %d, %Y, %I:%M %p')
        self.assertEqual(reports_data[0]['created_at'], expected_str)

    def test_report_create_view_non_standard_validation_error_def_06(self):
        self.client.login(username='student_view@campus.edu', password='password123')
        from reports.forms import ReportForm
        form = ReportForm(data={'latitude': 23.85, 'longitude': 90.5, 'category': ReportCategory.STAGNANT_WATER})
        self.assertFalse(form.is_valid())
        self.assertIn('Outside campus boundary', form.non_field_errors()[0])

