from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from .models import Role, RegisteredUser, Authority, Admin, Guest
from .permissions import resolve_actor, verify_actor_capability


class RoleAndCapabilityTests(TestCase):
    def setUp(self):
        self.user = RegisteredUser.objects.create_user(
            email='student@campus.edu',
            password='password123',
            full_name='Student Member',
            role=Role.REGISTERED
        )
        self.authority = RegisteredUser.objects.create_user(
            email='cleaner@campus.edu',
            password='password123',
            full_name='Campus Cleaning Authority',
            role=Role.AUTHORITY
        )
        self.admin = RegisteredUser.objects.create_user(
            email='admin@campus.edu',
            password='password123',
            full_name='Campus Admin',
            role=Role.ADMIN
        )

    def test_guest_capabilities(self):
        guest = Guest()
        self.assertTrue(guest.has_capability('view_heatmap'))
        self.assertTrue(guest.has_capability('login'))
        self.assertTrue(guest.has_capability('register'))
        self.assertFalse(guest.has_capability('submit_report'))
        self.assertFalse(guest.has_capability('accept_task'))
        self.assertFalse(guest.has_capability('verify_reports'))

    def test_registered_user_capabilities(self):
        actor = resolve_actor(self.user)
        self.assertTrue(actor.has_capability('view_heatmap'))
        self.assertTrue(actor.has_capability('submit_report'))
        self.assertFalse(actor.has_capability('accept_task'))
        self.assertFalse(actor.has_capability('verify_reports'))

    def test_authority_proxy_capabilities(self):
        actor = resolve_actor(self.authority)
        self.assertIsInstance(actor, Authority)
        self.assertTrue(actor.has_capability('view_heatmap'))
        self.assertTrue(actor.has_capability('submit_report'))
        self.assertTrue(actor.has_capability('accept_task'))
        self.assertTrue(actor.has_capability('upload_work_progress'))
        self.assertTrue(actor.has_capability('mark_area_clean'))
        # Admin action must NOT belong to Authority
        self.assertFalse(actor.has_capability('verify_reports'))
        self.assertFalse(actor.has_capability('assign_task'))

    def test_admin_proxy_capabilities(self):
        actor = resolve_actor(self.admin)
        self.assertIsInstance(actor, Admin)
        self.assertTrue(actor.has_capability('view_heatmap'))
        self.assertTrue(actor.has_capability('submit_report'))
        self.assertTrue(actor.has_capability('verify_reports'))
        self.assertTrue(actor.has_capability('assign_task'))
        # Authority action must NOT belong to Admin
        self.assertFalse(actor.has_capability('accept_task'))
        self.assertFalse(actor.has_capability('upload_work_progress'))

    def test_resolve_actor_for_anonymous_and_none(self):
        self.assertIsInstance(resolve_actor(None), Guest)
        self.assertIsInstance(resolve_actor(AnonymousUser()), Guest)

    def test_verify_actor_capability(self):
        # Should succeed without error
        verify_actor_capability(self.user, 'submit_report')

        # Should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            verify_actor_capability(self.user, 'verify_reports')

        with self.assertRaises(PermissionDenied):
            verify_actor_capability(None, 'submit_report')

    def test_resolve_actor_privilege_escalation_prevented_def_01(self):
        """Demoted user previously in Admin class must resolve to RegisteredUser."""
        demoted = Admin(role=Role.REGISTERED)
        actor = resolve_actor(demoted)
        self.assertIs(type(actor), RegisteredUser)
        self.assertFalse(actor.has_capability('verify_reports'))
        self.assertFalse(actor.has_capability('assign_task'))

    def test_case_insensitive_authentication_def_02(self):
        """Authentication must succeed regardless of email case casing."""
        user = RegisteredUser.objects.create_user(
            email='CaseUser@campus.edu',
            password='Password123!',
            full_name='Case Tester'
        )
        self.assertEqual(user.email, 'caseuser@campus.edu')
        self.assertIsNotNone(authenticate(username='CaseUser@campus.edu', password='Password123!'))
        self.assertIsNotNone(authenticate(username='caseuser@campus.edu', password='Password123!'))
        self.assertIsNotNone(authenticate(username='CASEUSER@CAMPUS.EDU', password='Password123!'))

    def test_proxy_model_role_assignment_and_manager_def_03(self):
        """Creating an Authority or Admin proxy model sets role and appears in manager."""
        auth = Authority.objects.create(email='auto_auth@campus.edu', full_name='Auto Auth')
        self.assertEqual(auth.role, Role.AUTHORITY)
        self.assertTrue(Authority.objects.filter(id=auth.id).exists())

        admin = Admin.objects.create(email='auto_admin@campus.edu', full_name='Auto Admin')
        self.assertEqual(admin.role, Role.ADMIN)
        self.assertTrue(Admin.objects.filter(id=admin.id).exists())

    def test_polymorphic_capabilities_property_d09(self):
        """RegisteredUser instance with role=ADMIN returns full admin capabilities."""
        admin_as_user = RegisteredUser.objects.get(id=self.admin.id)
        self.assertIn('verify_reports', admin_as_user.capabilities)
        self.assertIn('assign_task', admin_as_user.capabilities)

    def test_open_redirect_protection_def_05(self):
        """External domains in next parameter must be rejected."""
        # Test Login redirect
        login_res = self.client.post('/accounts/login/?next=https://malicious-phishing.com', {
            'email': 'student@campus.edu',
            'password': 'password123'
        })
        self.assertRedirects(login_res, '/', fetch_redirect_response=False)

        self.client.logout()

        # Test Register redirect
        reg_res = self.client.post('/accounts/register/?next=https://malicious-phishing.com', {
            'full_name': 'New Student',
            'email': 'new_student@campus.edu',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertRedirects(reg_res, '/', fetch_redirect_response=False)
