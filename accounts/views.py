from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import FormView, View

from .forms import LoginForm, RegistrationForm


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('heatmap')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('heatmap')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Welcome to Campus DengueWatch, {user.full_name}!')
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure()
        ):
            return redirect(next_url)
        return super().form_valid(form)


class UserLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('heatmap')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('heatmap')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.user)
        messages.success(self.request, f'Signed in as {form.user.full_name}.')
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure()
        ):
            return redirect(next_url)
        return super().form_valid(form)


class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'You have been signed out.')
        return redirect('heatmap')

    def get(self, request, *args, **kwargs):
        messages.warning(request, 'Please sign out using the navigation menu.')
        return redirect('heatmap')
