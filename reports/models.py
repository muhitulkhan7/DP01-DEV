from django.conf import settings
from django.db import models


class ReportStatus(models.TextChoices):
    VISIBLE = 'VISIBLE', 'Visible'
    HIDDEN = 'HIDDEN', 'Hidden'
    RESOLVED = 'RESOLVED', 'Resolved'


class ReportCategory(models.TextChoices):
    STAGNANT_WATER = 'STAGNANT_WATER', 'Stagnant Water'
    MANY_MOSQUITOES = 'MANY_MOSQUITOES', 'Many Mosquitoes'
    BITE_INCIDENT = 'BITE_INCIDENT', 'Bite Incident'


class ReportQuerySet(models.QuerySet):
    def active(self):
        """Returns only visible reports for public heatmap display."""
        return self.filter(status=ReportStatus.VISIBLE)


class Report(models.Model):
    """
    Mosquito activity report submitted by a registered user.
    """

    latitude = models.FloatField(verbose_name='Latitude')
    longitude = models.FloatField(verbose_name='Longitude')
    category = models.CharField(
        max_length=30,
        choices=ReportCategory.choices,
        verbose_name='Category'
    )
    note = models.TextField(blank=True, default='', verbose_name='Note')
    photo = models.ImageField(
        upload_to='reports/',
        blank=True,
        null=True,
        verbose_name='Photo'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.VISIBLE,
        verbose_name='Status'
    )
    resolved_note = models.TextField(blank=True, default='', verbose_name='Resolved Note')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Reporting User'
    )

    objects = ReportQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def hide(self):
        """Hides the report from the public heatmap (used in Phase 2 moderation)."""
        self.status = ReportStatus.HIDDEN
        self.save(update_fields=['status'])

    def mark_resolved(self, note: str = ''):
        """Marks the report as resolved upon work approval (Phase 2)."""
        self.status = ReportStatus.RESOLVED
        if note:
            self.resolved_note = note
        self.save(update_fields=['status', 'resolved_note'])

    def __str__(self):
        return f'{self.get_category_display()} at ({self.latitude}, {self.longitude}) [{self.status}]'
