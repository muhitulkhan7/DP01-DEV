from django.urls import path
from .views import HeatmapView, ReportCreateView

urlpatterns = [
    path('', HeatmapView.as_view(), name='heatmap'),
    path('report/', ReportCreateView.as_view(), name='report_create'),
]

