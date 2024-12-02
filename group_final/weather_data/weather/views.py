import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from .models import WeatherWeather, WeatherCity, WeatherCountry
from .forms import WeatherForm 
import pandas as pd

def all_weather(request):
        usa = WeatherCountry.objects.get(name="USA")
        cities = WeatherCity.objects.filter(country=usa).order_by('name')
        return render(request, 'all_weather.html', {'cities': cities})


def generate_graph(dates, temperatures, humidities, title, xlabel):
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.set_xlabel(xlabel)
    ax1.set_ylabel('Temperature (°F)', color='r')
    ax1.plot(dates, temperatures, color='r', label='Temperature')
    ax1.tick_params(axis='y', labelcolor='r')
    ax1.set_ylim(0, 100)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Humidity (%)', color='b')
    ax2.plot(dates, humidities, color='b', label='Humidity')
    ax2.tick_params(axis='y', labelcolor='b')
    ax2.set_ylim(0, 100)

    fig.tight_layout()
    plt.title(title)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close()
    return uri



def city_weather(request, city_id):
    weather_data = WeatherWeather.objects.filter(city_id=city_id).order_by('date')
    df = pd.DataFrame(list(weather_data.values('date', 'temperature', 'humidity')))
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Average temperature and humidity graph
    monthly_avg = df.resample('M').mean()
    average_graph = generate_graph(monthly_avg.index, monthly_avg['temperature'], monthly_avg['humidity'], 'Average Temperature and Humidity Per Month', 'Month')

    # Yearly temperature and humidity graphs
    year_graphs = {}
    for year in range(2015, 2024):
        yearly_data = df[df.index.year == year]
        if not yearly_data.empty:
            year_graphs[year] = generate_graph(yearly_data.index, yearly_data['temperature'], yearly_data['humidity'], f'Temperature and Humidity in {year}', 'Date')

    return render(request, 'city_weather.html', {
        'weather_data': weather_data,
        'average_graph': average_graph,
        'year2016_graph': year_graphs.get(2016, ''),
        'year2017_graph': year_graphs.get(2017, ''),
        
    })


def create_weather(request):
    if request.method == 'POST':
        form = WeatherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_weather')
    else:
        form = WeatherForm()
    return render(request, 'create_weather.html', {'form': form})

