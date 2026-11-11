from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Role(models.TextChoices):
    REGISTERED = 'REGISTERED', 'Registered User'
    AUTHORITY = 'AUTHORITY', 'Authority'
    ADMIN = 'ADMIN', 'Admin'


class Guest:
    """Non-database class representing an unauthenticated visitor."""

    capabilities = frozenset({
        'view_heatmap',
        'view_advisories',
        'view_mitigation_pins',
        'view_cleanup_events',
        'register',
        'login',
    })

    @property
    def is_authenticated(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities

    def __str__(self):
        return 'Guest'


class RegisteredUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required.')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class RegisteredUser(AbstractUser):
    """
    Parent user model with stored role field.
    Mapped fields: email (unique login identifier), full_name, password (Django hash), date_joined.
    """

    username = None
    email = models.EmailField(unique=True, verbose_name='Email Address')
    full_name = models.CharField(max_length=150, verbose_name='Full Name')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REGISTERED,
        verbose_name='User Role'
    )

    objects = RegisteredUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    base_capabilities = frozenset(Guest.capabilities | {
        'submit_report',
        'create_cleanup_event',
        'join_cleanup_event',
        'leave_cleanup_event',
        'take_questionnaire',
        'access_medical_portal',
        'logout',
    })

    @property
    def capabilities(self):
        actor = self.get_actor()
        if type(actor) is RegisteredUser:
            return self.base_capabilities
        return actor.capabilities

    def get_actor(self):
        from .permissions import resolve_actor
        return resolve_actor(self)

    def has_capability(self, capability: str) -> bool:
        return capability in self.get_actor().capabilities

    def __str__(self):
        return f'{self.full_name} ({self.email})'


class AuthorityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=Role.AUTHORITY)


class Authority(RegisteredUser):
    """
    Proxy model for Authority role (sibling of Admin).
    """

    objects = AuthorityManager()

    extra_capabilities = frozenset({
        'view_assigned_areas',
        'accept_task',
        'upload_work_progress',
        'mark_area_clean',
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'role' not in kwargs and not self.pk:
            self.role = Role.AUTHORITY

    def save(self, *args, **kwargs):
        if not self.role or ('role' not in kwargs and not self.pk and self.role == Role.REGISTERED):
            self.role = Role.AUTHORITY
        super().save(*args, **kwargs)

    @property
    def capabilities(self):
        return self.base_capabilities | self.extra_capabilities

    class Meta:
        proxy = True
        verbose_name = 'Authority'
        verbose_name_plural = 'Authorities'


class AdminManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=Role.ADMIN)


class Admin(RegisteredUser):
    """
    Proxy model for Admin role (sibling of Authority).
    """

    objects = AdminManager()

    extra_capabilities = frozenset({
        'manage_users',
        'verify_reports',
        'assign_task',
        'review_work',
        'manage_mitigation_pins',
        'remove_cleanup_event',
        'update_event_status',
        'post_advisory',
        'manage_doctor_portal',
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'role' not in kwargs and not self.pk:
            self.role = Role.ADMIN

    def save(self, *args, **kwargs):
        if not self.role or ('role' not in kwargs and not self.pk and self.role == Role.REGISTERED):
            self.role = Role.ADMIN
        super().save(*args, **kwargs)

    @property
    def capabilities(self):
        return self.base_capabilities | self.extra_capabilities

    class Meta:
        proxy = True
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
