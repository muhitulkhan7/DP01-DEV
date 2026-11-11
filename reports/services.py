from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.permissions import verify_actor_capability
from .models import Report


class ReportService:
    """
    Business logic service for mosquito activity reports.
    """

    @staticmethod
    def _is_point_in_polygon(lng: float, lat: float, ring: list) -> bool:
        """
        Ray-casting algorithm to test whether (lng, lat) is inside a polygon ring.
        ring is a list of [lng, lat] coordinate pairs.
        """
        n = len(ring)
        if n < 3:
            return False
        inside = False
        p1x, p1y = ring[0][0], ring[0][1]
        for i in range(1, n + 1):
            p2x, p2y = ring[i % n][0], ring[i % n][1]
            if lat > min(p1y, p2y):
                if lat <= max(p1y, p2y):
                    if lng <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or lng <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    @classmethod
    def validate_boundary(cls, lat: float, lng: float) -> bool:
        """
        Validates that the given coordinates are within the campus boundary.
        Supports both GeoJSON polygon geometry and bounding box limits.
        Raises ValidationError('Outside campus boundary') if outside.
        """
        boundary = getattr(settings, 'CAMPUS_BOUNDARY', {})

        # Fast rejection via bounding box if defined
        min_lat = boundary.get('min_lat')
        max_lat = boundary.get('max_lat')
        min_lng = boundary.get('min_lng')
        max_lng = boundary.get('max_lng')

        if (
            min_lat is not None and max_lat is not None and
            min_lng is not None and max_lng is not None
        ):
            if not (min_lat <= lat <= max_lat and min_lng <= lng <= max_lng):
                raise ValidationError('Outside campus boundary')

        # Precise GeoJSON polygon check if available
        geojson = boundary.get('geojson')
        if geojson:
            try:
                features = geojson.get('features', [])
                if features:
                    geom = features[0].get('geometry', {})
                else:
                    geom = geojson.get('geometry', geojson)

                if geom.get('type') == 'Polygon':
                    coordinates = geom.get('coordinates', [])
                    if coordinates:
                        outer_ring = coordinates[0]
                        if not cls._is_point_in_polygon(lng, lat, outer_ring):
                            raise ValidationError('Outside campus boundary')
            except (IndexError, KeyError, TypeError):
                pass

        return True

    @staticmethod
    def check_rate_limit(user) -> bool:
        """
        Validates that the user has not exceeded the daily report rate limit
        for the current local calendar day.
        Raises ValidationError('Too many reports today') if exceeded.
        """
        today = timezone.localdate()
        daily_limit = getattr(settings, 'DAILY_REPORT_LIMIT', 8)

        count = Report.objects.select_for_update().filter(
            user=user,
            created_at__date=today
        ).count()

        if count >= daily_limit:
            raise ValidationError('Too many reports today')

        return True

    @classmethod
    def create_report(cls, user, data, files=None) -> Report:
        """
        Creates a new mosquito activity report.
        Enforces:
        1. User capability (must be logged in with 'submit_report')
        2. Boundary check ('Outside campus boundary')
        3. Rate limit check ('Too many reports today')
        """
        verify_actor_capability(user, 'submit_report')

        try:
            lat = float(data.get('latitude'))
            lng = float(data.get('longitude'))
        except (TypeError, ValueError):
            raise ValidationError('Valid coordinates are required.')

        cls.validate_boundary(lat, lng)

        photo = files.get('photo') if files else data.get('photo')
        note = (data.get('note') or '').strip()

        with transaction.atomic():
            cls.check_rate_limit(user)
            report = Report(
                user=user,
                latitude=lat,
                longitude=lng,
                category=data.get('category'),
                note=note,
                photo=photo
            )
            report.save()
        return report

    @classmethod
    def hide_report(cls, admin, report: Report) -> Report:
        """
        Hides a report from the public map. Enforces admin capability.
        """
        verify_actor_capability(admin, 'verify_reports')
        report.hide()
        return report

