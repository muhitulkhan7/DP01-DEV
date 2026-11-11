from django import forms
from django.core.exceptions import ValidationError

from .models import Report, ReportCategory
from .services import ReportService


class ReportForm(forms.ModelForm):
    """
    ModelForm for submitting a mosquito activity report.
    """

    latitude = forms.FloatField(
        widget=forms.HiddenInput(attrs={'id': 'id_latitude'}),
        required=True
    )
    longitude = forms.FloatField(
        widget=forms.HiddenInput(attrs={'id': 'id_longitude'}),
        required=True
    )
    category = forms.ChoiceField(
        choices=ReportCategory.choices,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'id_category',
            'required': 'required'
        }),
        required=True,
        label='Activity Category'
    )
    note = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional details (e.g. location cues, water container type)',
            'id': 'id_note'
        }),
        required=False,
        label='Optional Note'
    )
    photo = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_photo'
        }),
        required=False,
        label='Optional Photo (Camera / Gallery)'
    )

    class Meta:
        model = Report
        fields = ['category', 'note', 'photo', 'latitude', 'longitude']

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')

        if lat is None or lng is None:
            raise ValidationError('Please select a location on the campus map.')

        try:
            ReportService.validate_boundary(lat, lng)
        except ValidationError as e:
            self.add_error(None, e)

        return cleaned_data

