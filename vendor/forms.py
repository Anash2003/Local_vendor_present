"""
Forms for vendor profile, services, and availability management.
"""

from django import forms
from services.models import Service, ServiceCategory


class VendorProfileEditForm(forms.Form):
    """Form for vendors to edit their profile and business details."""
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    business_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    business_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3})
    )
    business_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    pincode = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )


class ServiceForm(forms.ModelForm):
    """Form for vendors to add or edit services."""
    class Meta:
        model = Service
        fields = ['category', 'name', 'description', 'price', 'duration_minutes', 'is_available']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Service Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Price in ₹'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Duration in minutes'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active categories in the dropdown
        self.fields['category'].queryset = ServiceCategory.objects.filter(is_active=True)


class AvailabilityForm(forms.Form):
    """Form for vendors to set availability for a day."""
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    day_of_week = forms.ChoiceField(
        choices=DAY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'})
    )
    is_available = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError('End time must be after start time.')
        return cleaned_data

