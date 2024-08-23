# prices/views.py

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .models import Medicine, Price
from .serializers import MedicineSerializer, PriceSerializer
from django.http import JsonResponse
from .webscrape import get_ifood_price, get_drogasil_price, get_price_globo, get_price_paguemenos
import concurrent.futures
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from time import sleep

@api_view(['GET'])
def ifood_view(request, name):
    cep = request.query_params.get('cep', '')
    price = get_ifood_price(name, cep)
    
    if price is None:
        return Response({"error": "No prices found for the product on iFood"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'name': name,
        'lowest_price': price
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def drogasil_view(request, name):
    price = get_drogasil_price(name)

    if price is None:
        return Response({"error": "No prices found for the product on Drogasil"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'name': name,
        'lowest_price': price
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def paguemenos_view(request, name):
    price = get_price_paguemenos(name, "Pague Menos")
    
    if price is None:
        return Response({"error": "No prices found for the product on Pague Menos"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'name': name,
        'lowest_price': price
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def globo_view(request, name):
    price = get_price_globo(name, "Drogaria Globo")

    if price is None:
        return Response({"error": "No prices found for the product on Drogaria Globo"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'name': name,
        'lowest_price': price
    }, status=status.HTTP_200_OK)