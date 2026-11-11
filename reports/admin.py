from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'status', 'user', 'latitude', 'longitude', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('note', 'user__email', 'user__full_name')
