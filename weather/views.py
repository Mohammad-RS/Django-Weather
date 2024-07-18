from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.conf import settings
import requests, datetime, collections, pandas, os
from django.views.generic import View, TemplateView

from .forms import AddCityForm

class IndexView(View):
    def get_response(self, url):
        return requests.get(url)
    
    def get(self, request):
        today = timezone.localdate(timezone.now())
        cities = request.session.get('cities', '')
        API_key = 'd12b11fc3c67e9387aa256613a36acbc'
        form = AddCityForm
        all_weathers = []
        """
        for path in settings.STATICFILES_DIRS:
            try: file_path = os.path.join(path, 'weather/worldcities.csv') # STATIC_URL after collection
            except: pass
        columns_to_read = ['city']
        world_cities = pandas.read_csv(file_path, usecols=columns_to_read).to_dict()
        """
        
        def get_next_3_days(today):
            next_3_days = [today + datetime.timedelta(days=i) for i in range(1, 4)]
            return next_3_days

        def get_next_3_days_weather(next_3_days, city_forecast):
            next_3_days_weather = [] 
            today_weather = [[], [], [], [], [], []] # Avg Temp - Weather Condition - Weather Icon - Humidity - Visibility - Wind Speed 
            
            for day in next_3_days:
                for report in city_forecast['list']:  
                    time_period = report['dt_txt']
                    if str(day) in time_period and f'{day} 21:00:00' != time_period:
                        today_weather[0].append(int(report['main']['temp']))
                        """
                        today_weather[1].append(report['weather'][0]['main'])
                        today_weather[2].append(report['weather'][0]['icon'])
                        today_weather[3].append(report['main']['humidity'])
                        today_weather[4].append(report['visibility'])
                        today_weather[5].append(report['wind']['speed'])
                        """
                    elif f'{day} 21:00:00' == time_period:
                        today_weather[0].append(int(report['main']['temp']))
                        temp_max, temp_min = max(today_weather[0]), min(today_weather[0])
                        """
                        today_weather[1].append(report['weather'][0]['main'])
                        today_weather[2].append(report['weather'][0]['icon'])
                        today_weather[3].append(int(report['main']['humidity']))
                        today_weather[4].append(report['visibility'])
                        today_weather[5].append(report['wind']['speed'])
                        today_weather_overall = collections.Counter(today_weather[1]).most_common(1)[0][0]
                        today_icon_overall = collections.Counter(today_weather[2]).most_common(1)[0][0]
                        """
                        next_3_days_weather.append({
                                'today_short': day.strftime('%a'), 'temp_max': temp_max, 'temp_min': temp_min,
                                #'today_date': str(day), 'today': day.strftime('%A'), 
                                #'city': city_forecast['city']['name'], 'country': city_forecast['city']['country'],
                                #'weather' : today_weather_overall, 'icon': get_icon(today_icon_overall),
                                #'temp': round((temp_max + temp_min) / 2), 
                                #'humidity': (sum(today_weather[3])/8), 'visibility': round(sum(today_weather[4]) / 800),
                                #'wind_speed': round((sum(today_weather[5]) / 8) * 3.6, 1), 
                            })
                        today_weather = [[], [], [], [], [], []] # temps weather icon hum vis wind 
                    else: pass
                    
            return next_3_days_weather

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
        
        def get_weathers(cities):
            for city in cities:
                city_weather = self.get_response(f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_key}').json()
                city_forecast = self.get_response(f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&cnt=40&appid={API_key}').json()
                icon = get_icon(city_weather['weather'][0]['icon'])
                next_3_days = get_next_3_days_weather(get_next_3_days(today), city_forecast)
                context = {
                    'country': city_weather['sys']['country'], 'city': city, 
                    'weather': city_weather['weather'][0]['main'], 'icon': icon, 
                    'temp': round(city_weather['main']['temp']), 
                    'humidity': city_weather['main']['humidity'], 'visibility': round(city_weather['visibility'] / 100), 
                    'wind_speed': round(city_weather['wind']['speed'] * 3.6, 1), 
                    'next_3_days': next_3_days, 
                    }
                all_weathers.append(context)
            return all_weathers
        return render(request, 'weather/index.html', context = {
                    'cities': get_weathers(cities), 'form': form, #'world_cities': world_cities,
                    'today': today.strftime('%A'), 'today_date':today, 'today_short': today.strftime('%a'),
                    })
    
    def post(self, request):

        
        form = AddCityForm(request.POST)
        if form.is_valid():    
            API_key = 'd12b11fc3c67e9387aa256613a36acbc'
            city = form.cleaned_data.get('city', None)
            city_weather = self.get_response(f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_key}')
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

        
# !Maybe Add a seach and select form for adding cities
# !Maybe Add location based search on user authentication

