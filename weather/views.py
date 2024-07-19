from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
import requests, datetime, collections
from django.views.generic import View

from .forms import AddCityForm

class IndexView(View):
    def get_api_response(self, url):
        return requests.get(url)
    
    def get(self, request):
        today = timezone.localdate(timezone.now())
        cities = request.session.get('cities', '')
        weather_data = []
        
        def get_next_3_days(today):
            next_3_days = [today + datetime.timedelta(days=i) for i in range(1, 4)]
            return next_3_days

        def get_icon(weather_icon):
            icons = {
                '01d': 'sun.png', '01n': 'moon.png',
                '02': 'cloud.png', '03': 'rain-cloud.png', '04': 'cloud-off.png',
                '09': 'cloud-rain.png', '10': 'cloud-drizzle.png', '11': 'cloud-lighning.png', '13': 'cloud-snow.png',
                '50': 'wind.png',
                }
            for key in icons.keys():
                if key in weather_icon:
                    return icons[key]
        
        def get_next_3_days_weather(next_3_days, city_forecast):
            next_3_days_reports = []             
            next_3_days_weather_data = []   
            
            for report in city_forecast['list']:
                next_3_days_reports.append((report['dt_txt'], round(report['main']['temp']), report['weather'][0]['icon']))
                        
            for day in next_3_days:
                daily_temps = [] 
                daily_icons = []
                for report in next_3_days_reports:
                    if str(day) in report[0]:
                        if f'{day} 21:00:00' == report[0]:
                            daily_temps.append(report[1])   
                            daily_icons.append(report[2])
                        else:
                            daily_temps.append(report[1])   
                            daily_icons.append(report[2])
                next_3_days_weather_data.append({
                    'today_short': day.strftime('%a'), 'temp_max': max(daily_temps), 'temp_min': min(daily_temps),
                    'icon': get_icon(collections.Counter(daily_icons).most_common(1)[0][0]),
                    })
                
            return next_3_days_weather_data            
        
        def get_weathers(cities):
            API_key = 'd12b11fc3c67e9387aa256613a36acbc'
            
            for city in cities:
                city_weather = self.get_api_response(f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_key}').json()
                city_forecast = self.get_api_response(f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&cnt=32&appid={API_key}').json()
                context = {
                    'country': city_weather['sys']['country'], 'city': city, 
                    'weather': city_weather['weather'][0]['main'], 'icon': get_icon(city_weather['weather'][0]['icon']), 
                    'temp': round(city_weather['main']['temp']), 
                    'humidity': city_weather['main']['humidity'], 'visibility': round(city_weather['visibility'] / 100), 
                    'wind_speed': round(city_weather['wind']['speed'] * 3.6, 1), 
                    'next_3_days': get_next_3_days_weather(get_next_3_days(today), city_forecast), 
                    }
                weather_data.append(context)
                
            return weather_data
        
        return render(request, 'weather/index.html', context = {
                    'cities': get_weathers(cities), 'form': AddCityForm,
                    'today': today.strftime('%A'), 'today_date':today, 'today_short': today.strftime('%a'),
                    })
    
    def post(self, request):
        form = AddCityForm(request.POST)
        
        if form.is_valid():    
            API_key = 'd12b11fc3c67e9387aa256613a36acbc'
            city = form.cleaned_data.get('city', None)
            city_weather = self.get_api_response(f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_key}')
            if city_weather.status_code == 200:
                cities = request.session.get('cities', [])
                cities.insert(0, city)
                request.session['cities'] = cities
            else: pass
            return redirect(reverse_lazy('index'))
        else: 
            return redirect(reverse_lazy('index'))

class CityDeleteView(View):
    def post(self, request):
        city_name = request.POST.get('city_name', None)        
        cities = request.session.get('cities')
        try:
            cities.remove(city_name)
        except:
            pass
        request.session['cities'] = cities
        return redirect(reverse_lazy('index'))
