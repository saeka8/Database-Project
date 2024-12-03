import matplotlib,urllib, base64,json
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from django.shortcuts import render, redirect
from django.db.models import Avg
from .models import WeatherWeather, WeatherCity, WeatherCountry
from .forms import WeatherForm 

def all_weather(request):
        usa = WeatherCountry.objects.get(name="USA")
        cities = WeatherCity.objects.filter(country=usa).order_by('name')
        weather_data = None
        selected_city = None
        if request.method == 'POST':
            city_id = request.POST.get('city')
            if city_id:
                selected_city = WeatherCity.objects.get(id=city_id)
                weather_data = WeatherWeather.objects.filter(city_id=city_id).order_by('date')
                for data in weather_data:
                    data.temperature_celsius = (data.temperature - 32) * 5.0/9.0
        return render(request, 'all_weather.html', {
            'cities': cities,
            'weather_data': weather_data,
            'selected_city': selected_city,
        })


def generate_graph(dates, temperatures, humidities, title, xlabel):
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.set_xlabel(xlabel)
    ax1.set_ylabel('Temperature (°F)', color='r')
    ax1.plot(dates, temperatures, 'r-')
    ax1.tick_params(axis='y', labelcolor='r')
    ax1.set_ylim(0,100)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Humidity (%)', color='b')
    ax2.plot(dates, humidities, 'b-')
    ax2.tick_params(axis='y', labelcolor='b')
    ax2.set_ylim(0,100)

    plt.title(title)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close()
    return uri

def city_weather(request, city_id):
    weather_data = WeatherWeather.objects.filter(city_id=city_id).order_by('date')
    city = WeatherCity.objects.get(id=city_id)
    df = pd.DataFrame(list(weather_data.values('date', 'temperature', 'humidity')))
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Calculate monthly averages across all years
    monthly_avg = df.groupby(df.index.month).mean()
    monthly_avg.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Calculate the correlation between temperature and humidity
    correlation = monthly_avg['temperature'].corr(monthly_avg['humidity'])

    # Prepare data to send to the template
    dates = monthly_avg.index.tolist()
    avg_temps = monthly_avg['temperature'].tolist()
    avg_humidities = monthly_avg['humidity'].tolist()

    return render(request, 'city_weather.html', {
        'city': city,
        'dates': json.dumps(dates),
        'avg_temps': json.dumps(avg_temps),
        'avg_humidities': json.dumps(avg_humidities),
        'correlation': correlation,  # pass correlation value to the template
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

def weather_visualization(request):
    city_filter = request.GET.get('city', None)

    queryset = WeatherWeather.objects.values('city__name').annotate(
        avg_temp=Avg('temperature'),
        avg_humidity=Avg('humidity')
    )

    if city_filter:
        queryset = queryset.filter(city__name=city_filter)

    data = queryset

    cities = [item['city__name'] for item in data]
    avg_temps = [item['avg_temp'] for item in data]
    avg_humidities = [item['avg_humidity'] for item in data]
    all_cities = list(set([item['city__name'] for item in data]))  

    return render(request, 'visualization.html', {
        'cities': json.dumps(cities),
        'avg_temps': json.dumps(avg_temps),
        'avg_humidities': json.dumps(avg_humidities),
        'all_cities': all_cities,  
        'selected_city': city_filter  
    })

def edit_weather(request, pk):
    weather = WeatherWeather.objects.get(pk=pk)
    if request.method == 'POST':
        form = WeatherForm(request.POST, instance=weather)
        if form.is_valid():
            form.save()
            return redirect('all_weather')
    else:
        form = WeatherForm(instance=weather)
    return render(request, 'edit_weather.html', {'form': form})

def delete_weather(request, pk):
    weather = WeatherWeather.objects.get(pk=pk)
    if request.method == 'POST':
        weather.delete()
        return redirect('all_weather')
    return render(request, 'delete_weather.html', {'weather': weather})

