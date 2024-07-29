# prices/urls.py

from django.urls import path
from .views import get_medicine_prices

urlpatterns = [
    path('medicines/<str:name>/prices/', get_medicine_prices, name='get_medicine_prices'),
]