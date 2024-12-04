"""
URL configuration for weather project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import all_weather, create_weather, city_weather, weather_visualization, edit_weather,delete_weather

urlpatterns = [
    path('', all_weather, name='all_weather'),
    path('edit/<int:pk>/', edit_weather, name='edit_weather'),
    path('delete/<int:pk>/', delete_weather, name='delete_weather'),
    path('create/', create_weather, name='create_weather'),
    path('city_weather/<int:city_id>/', city_weather, name='city_weather'),
    path('visualization/',weather_visualization,name ='weather_visualization'),

]
