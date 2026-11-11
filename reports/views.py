from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView

from accounts.permissions import ActorCapabilityMixin
from .forms import ReportForm
from .models import Report
from .services import ReportService


class HeatmapView(ActorCapabilityMixin, TemplateView):
    """
    Public heatmap page. Renders real-time (latest on page load) active reports.
    Accessible to Guests and all authenticated users.
    """

    template_name = 'reports/heatmap.html'
    required_capability = 'view_heatmap'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_reports = Report.objects.active()

        reports_data = [
            {
                'id': r.id,
                'lat': r.latitude,
                'lng': r.longitude,
                'category': r.get_category_display(),
                'category_code': r.category,
                'note': r.note,
                'photo_url': r.photo.url if r.photo else None,
                'created_at': timezone.localtime(r.created_at).strftime('%b %d, %Y, %I:%M %p'),
            }
            for r in active_reports
        ]

        context['reports_data'] = reports_data
        context['campus_boundary'] = getattr(settings, 'CAMPUS_BOUNDARY', {})
        context['report_count'] = len(reports_data)
        return context


class ReportCreateView(ActorCapabilityMixin, FormView):
    """
    Mosquito activity reporting page.
    Requires 'submit_report' capability (Logged in RegisteredUser, Authority, or Admin).
    """

    template_name = 'reports/report_form.html'
    form_class = ReportForm
    success_url = reverse_lazy('heatmap')
    required_capability = 'submit_report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campus_boundary'] = getattr(settings, 'CAMPUS_BOUNDARY', {})
        return context

    def form_valid(self, form):
        try:
            ReportService.create_report(
                user=self.request.user,
                data=form.cleaned_data,
                files=self.request.FILES
            )
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

        messages.success(self.request, 'Report submitted successfully.')
        return redirect(self.success_url)
