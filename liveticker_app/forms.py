from django import forms
from .models import LiveTicker, LiveTickerEvent

class LiveTickerForm(forms.ModelForm):
    class Meta:
        model = LiveTicker
        fields = ['title', 'description', 'ticker_type']

class LiveTickerEventForm(forms.ModelForm):
    class Meta:
        model = LiveTickerEvent
        fields = ['time', 'title', 'text', 'link', 'link_label']
        widgets = {
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full p-2 border rounded'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Titel des Ereignisses'
            }),
            'text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Beschreibung / Inhalt'
            }),
            'link': forms.URLInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'https://… (optional)'
            }),
            'link_label': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Link-Text (optional)'
            }),
        }

