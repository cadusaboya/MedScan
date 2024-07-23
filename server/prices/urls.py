# prices/urls.py

from django.urls import path
from .views import get_medicine_prices, add_price_to_medicine

urlpatterns = [
    path('medicines/<str:name>/prices/', get_medicine_prices, name='get_medicine_prices'),
    path('medicines/<str:name>/prices/add/', add_price_to_medicine, name='add_price_to_medicine'),
]