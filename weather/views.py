from django.shortcuts import render
from django.http import JsonResponse
from .models import SearchHistory
from django.views.decorators.http import require_GET
from django.db import models
from .utils import weather_code_to_desc
import requests
from datetime import datetime, timedelta
import pytz

def index(request):
    city = request.GET.get('city')
    weather = None
    error = None
    hourly_forecast = []

    # Получаем ключ сессии
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    # Получаем последний город из сессии (если есть)
    last_city = request.session.get('last_city')

    if city:
        try:
            geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json'
            geo_response = requests.get(geo_url).json()

            if 'results' in geo_response and geo_response['results']:
                latitude = geo_response['results'][0]['latitude']
                longitude = geo_response['results'][0]['longitude']
                timezone = geo_response['results'][0].get('timezone', 'UTC')  # Добавляем timezone

                weather_url = (
                    f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}'
                    f'&hourly=temperature_2m,weathercode&timezone={timezone}'
                )
                weather_response = requests.get(weather_url).json()

                if 'hourly' in weather_response:
                    times = weather_response['hourly']['time']  # Список строк ISO datetime
                    temps = weather_response['hourly']['temperature_2m']
                    codes = weather_response['hourly']['weathercode']

                    # Получаем текущее время в часовом поясе города
                    city_tz = pytz.timezone(timezone)
                    now = datetime.now(city_tz)

                    hourly_forecast = []
                    for time_str, temp, code in zip(times, temps, codes):
                        dt = datetime.fromisoformat(time_str)  # naive datetime
                        dt = city_tz.localize(dt)  # делаем aware с нужным timezone

                        if dt >= now and len(hourly_forecast) < 8:  # сравниваем aware объекты
                            hourly_forecast.append({
                                'time': dt.strftime('%Y-%m-%d %H:%M'),
                                'temperature': temp,
                                'description': weather_code_to_desc(code),
                            })
                weathercode = weather_response['current_weather']['weathercode']
                weather = {
                    'temperature': weather_response['current_weather']['temperature'],
                    'description': weather_code_to_desc(weathercode),
                }
                # Сохраняем город в сессию
                request.session['last_city'] = city

                # Записываем в историю поиска
                obj, created = SearchHistory.objects.get_or_create(session_key=session_key, city=city)
                if not created:
                    obj.count += 1
                    obj.save()

            else:
                error = "Город не найден"
        except Exception as e:
            error = f"Ошибка получения данных: {e}"

    return render(request, 'weather/index.html', {
    'city': city or last_city,
    'hourly_forecast': hourly_forecast,
    'error': error,
    'last_city': last_city,
    })

def autocomplete(request):
    query = request.GET.get('term', '')
    results = []

    if query:
        geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=ru&format=json'
        response = requests.get(geo_url)
        data = response.json()

        if 'results' in data:
            for item in data['results']:
                results.append(item['name'])

    return JsonResponse(results, safe=False)

def stats(request):
    data = (
        SearchHistory.objects
        .values('city')
        .annotate(total_count=models.Sum('count'))
        .order_by('-total_count')[:20]
    )

    stats_list = list(data)
    return JsonResponse(stats_list, safe=False)