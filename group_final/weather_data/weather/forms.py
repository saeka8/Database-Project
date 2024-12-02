# forms.py
from django import forms
from .models import WeatherWeather, WeatherCity

class WeatherForm(forms.ModelForm):
    class Meta:
        model = WeatherWeather
        fields = ['city','date', 'temperature', 'humidity']
        widgets = {
            'city': forms.Select(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = WeatherCity.objects.order_by('name')
