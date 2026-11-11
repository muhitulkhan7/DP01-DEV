from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import RegisteredUserChangeForm, RegisteredUserCreationForm
from .models import RegisteredUser, Authority, Admin, Role


@admin.register(RegisteredUser)
class RegisteredUserAdmin(BaseUserAdmin):
    form = RegisteredUserChangeForm
    add_form = RegisteredUserCreationForm

    ordering = ('email',)
    list_display = ('email', 'full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'full_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Authority)
class AuthorityAdmin(RegisteredUserAdmin):
    list_display = ('email', 'full_name', 'is_active', 'date_joined')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        obj.role = Role.AUTHORITY
        super().save_model(request, obj, form, change)


@admin.register(Admin)
class AdminUserAdmin(RegisteredUserAdmin):
    list_display = ('email', 'full_name', 'is_active', 'date_joined')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        obj.role = Role.ADMIN
        super().save_model(request, obj, form, change)
