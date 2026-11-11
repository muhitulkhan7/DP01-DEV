from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import RegisteredUser, Role


class RegisteredUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = RegisteredUser
        fields = ('email', 'full_name', 'role')


class RegisteredUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = RegisteredUser
        fields = '__all__'


class RegistrationForm(forms.ModelForm):
    """
    Form for registering a new student/campus member.
    """

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Full Name',
            'autocomplete': 'name',
            'required': 'required'
        }),
        label='Full Name'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'campus_id@university.edu',
            'autocomplete': 'email',
            'required': 'required'
        }),
        label='Campus Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
            'required': 'required'
        }),
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
            'required': 'required'
        }),
        label='Confirm Password'
    )

    class Meta:
        model = RegisteredUser
        fields = ['full_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if RegisteredUser.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.role = Role.REGISTERED
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    Form for logging in with campus email.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'campus_id@university.edu',
            'autocomplete': 'email',
            'required': 'required'
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
            'required': 'required'
        }),
        label='Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').strip().lower()
        password = cleaned_data.get('password')

        if email and password:
            self.user = authenticate(username=email, password=password)
            if not self.user:
                raise ValidationError('Invalid email or password.')

        return cleaned_data

