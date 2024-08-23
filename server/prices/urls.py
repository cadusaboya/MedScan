# prices/urls.py

from django.urls import path
from .views import ifood_view, drogasil_view, globo_view, paguemenos_view

urlpatterns = [
    path('ifood/<str:name>/', ifood_view, name='ifood_webscrape'),
    path('drogasil/<str:name>/', drogasil_view, name='drogasil_webscrape'),
    path('globo/<str:name>/', globo_view, name='globo_webscrape'),
    path('paguemenos/<str:name>/', paguemenos_view, name='paguemenos_webscrape'),
]