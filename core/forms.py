from django import forms
from .models import Event, Session

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'date', 'image_url', 'image_alt_text']
        labels = {
            'image_url': 'Cover Image URL',
            'image_alt_text': 'Image Description (for accessibility)',
        }
        help_texts = {
            'image_url': 'Paste a link to an image that represents your event.',
            'image_alt_text': 'Briefly describe the image for visually impaired users.',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://example.com/image.jpg', 'class': 'form-control'}),
            'image_alt_text': forms.TextInput(attrs={'placeholder': 'e.g., A group of students collaborating', 'class': 'form-control'}),
        }

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['title', 'start_time', 'end_time', 'capacity']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }