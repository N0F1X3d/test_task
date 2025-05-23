from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from weather.models import SearchHistory
from weather.views import weather_code_to_desc

class MockResponse:
    def __init__(self, json_data):
        self.json_data = json_data
    def json(self):
        return self.json_data

class WeatherViewTests(TestCase):

    @patch('weather.views.requests.get')
    def test_index_view_structure(self, mock_get):
        city = 'Москва'

        # Мокаем геокодинг — всегда возвращаем координаты и таймзону
        geo_response = {
            'results': [{
                'latitude': 55.75,
                'longitude': 37.62,
                'timezone': 'Europe/Moscow'
            }]
        }

        # Мокаем прогноз — 24 часа подряд, чтобы покрыть любой "текущий час"
        hourly_response = {
            'hourly': {
                'time': [f'2025-05-23T{str(h).zfill(2)}:00' for h in range(24)],
                'temperature_2m': list(range(24)),
                'weathercode': [0]*24,  # Используем weathercode=0 для простоты
            },
            'current_weather': {
                'temperature': 20,
                'weathercode': 0
            }
        }

        mock_get.side_effect = [
            MockResponse(geo_response),       # первый вызов — геокодинг
            MockResponse(hourly_response)     # второй вызов — прогноз
        ]

        response = self.client.get(reverse('index'), {'city': city})

        self.assertEqual(response.status_code, 200)

        # Проверяем, что в контексте есть hourly_forecast — список с элементами-словарями
        hourly = response.context['hourly_forecast']
        self.assertIsInstance(hourly, list)
        self.assertTrue(0 < len(hourly) <= 8)  # Выбрано максимум 8 элементов

        first_item = hourly[0]
        self.assertIsInstance(first_item, dict)
        self.assertIn('time', first_item)
        self.assertIn('temperature', first_item)
        self.assertIn('description', first_item)

        # Проверяем, что description соответствует weather_code_to_desc для кода 0
        self.assertEqual(first_item['description'], weather_code_to_desc(0))

        # Проверяем, что в сессии сохранён последний город
        self.assertEqual(response.wsgi_request.session.get('last_city'), city)

        # Проверяем, что в БД добавлена запись поиска с правильным session_key и городом
        session_key = response.wsgi_request.session.session_key
        self.assertTrue(SearchHistory.objects.filter(session_key=session_key, city=city).exists())

        # Проверяем, что город есть в отрендеренном HTML
        content = response.content.decode()
        self.assertIn(city, content)
