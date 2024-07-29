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

@api_view(['GET'])
def get_medicine_prices(request, name):
    cep = request.query_params.get('cep', '')

    # Create a function that handles each price-fetching task
    def fetch_price(func, *args):
        try:
            price = func(*args)
            return price
        except Exception as e:
            return None

    # Initialize the prices dictionary
    prices = {}

    # List of functions and their respective arguments
    tasks = [
        (get_price_globo, name, "Drogaria Globo"),
        (get_price_paguemenos, name, "Pague Menos"),
        (get_drogasil_price, name),
        (get_ifood_price, name, cep)
    ]

    # Use ThreadPoolExecutor to run tasks concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks to the executor
        future_to_task = {executor.submit(fetch_price, func, *args): func.__name__ for func, *args in tasks}
        
        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(future_to_task):
            result = future.result()
            if result:  # If the result is not None, update the prices dictionary
                prices.update(result)

    # Filter out None values and return the prices
    valid_prices = {provider: price for provider, price in prices.items() if price is not None}

    if not valid_prices:
        return Response({"error": "No prices found for the product"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'name': name,
        'lowest_prices': valid_prices
    }, status=status.HTTP_200_OK)