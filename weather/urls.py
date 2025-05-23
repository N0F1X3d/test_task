from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), #главная
    path('autocomplete/', views.autocomplete, name='autocomplete'),  # подсказки
    path('stats/', views.stats, name='stats') #статистика запросов
]
