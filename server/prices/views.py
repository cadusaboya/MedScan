# prices/views.py

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .models import Medicine, Price
from .serializers import MedicineSerializer, PriceSerializer
from django.http import JsonResponse
from .webscrape import get_ifood_price, get_drogasil_price, get_price_globo, get_price_paguemenos

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def get_medicine_prices(request, name):
    cep = request.query_params.get('cep', '')

    # Initialize a dictionary to store the lowest prices from each provider
    prices = {}

    try:
        globo_price = get_price_globo(name, "Drogaria Globo")
        if globo_price:
            prices.update(globo_price)
    except Exception as e:
        print(f"Failed to find Globo price: {str(e)}")

    try:
        paguemenos_price = get_price_paguemenos(name, "Pague Menos")
        if paguemenos_price:
            prices.update(paguemenos_price)
    except Exception as e:
        print(f"Failed to find Pague Menos price: {str(e)}")

    try:
        drogasil_price = get_drogasil_price(name)
        if drogasil_price:
            prices.update(drogasil_price)
    except Exception as e:
        print(f"Failed to find Drogasil price: {str(e)}")

    try:
        ifood_price = get_ifood_price(name, cep)
        if ifood_price:
            prices.update(ifood_price)
    except Exception as e:
        print(f"Failed to find iFood price: {str(e)}")

    # Filter out None values and return the prices
    valid_prices = {provider: price for provider, price in prices.items() if price is not None}

    if not valid_prices:
        return Response({"error": "No prices found for the product"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'name': name,
        'lowest_prices': valid_prices
    }, status=status.HTTP_200_OK)