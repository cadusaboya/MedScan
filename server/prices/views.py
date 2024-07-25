# prices/views.py

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .models import Medicine, Price
from .serializers import MedicineSerializer, PriceSerializer
from django.http import JsonResponse
from .webscrape import get_ifood_price, get_drogasil_price, get_price_globo, get_price_paguemenos

@api_view(['GET'])
def get_medicine_prices(request, name):
    try:
        medicine = Medicine.objects.get(name=name)
    except Medicine.DoesNotExist:
        return Response({"error": "Medicine not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MedicineSerializer(medicine)
    return Response(serializer.data)

@api_view(['POST'])
def add_price_to_medicine(request, name):
    # Try to get the existing medicine, or create a new one
    medicine, created = Medicine.objects.get_or_create(name=name)
    
    # Extract CEP and company_name from the request data if available
    cep = request.data.get('cep', '')


    # Fetch prices from webscraping functions
    try:
        globo_price = get_price_globo(name, "Drogaria Globo")
    except Exception as e:
        print(f"Failed to find price: {str(e)}")
        globo_price = {'Globo': 0}
    try:
        paguemenos_price = get_price_paguemenos(name, "Pague Menos")
    except Exception as e:
        print(f"Failed to find price: {str(e)}")
        paguemenos_price = {'Pague Menos': 0}
    try:
        drogasil_price = get_drogasil_price(name)
    except Exception as e:
        print(f"Failed to find price: {str(e)}")
        drogasil_price = {'Drogasil': 0}
    try:
        ifood_price = get_ifood_price(name, cep)
    except Exception as e:
        print(f"Failed to find price: {str(e)}")
        ifood_price = {'iFood': 0}
    
    # Prepare prices data for saving
    prices_data = []

    for provider, price in ifood_price.items():
        prices_data.append({
            'medicine': medicine.id,
            'provider': provider,
            'price': price
        })

    for provider, price in drogasil_price.items():
        prices_data.append({
            'medicine': medicine.id,
            'provider': provider,
            'price': price
        })

    for provider, price in globo_price.items():
        prices_data.append({
            'medicine': medicine.id,
            'provider': provider,
            'price': price
        })

    for provider, price in paguemenos_price.items():
        prices_data.append({
            'medicine': medicine.id,
            'provider': provider,
            'price': price
        })
    
    # Create and save Price objects
    for price_data in prices_data:
        serializer = PriceSerializer(data=price_data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': 'Prices added successfully'}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_medicine_price(request, name):
    medicine = Medicine.objects.filter(name=name).first()
    if not medicine:
        return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)
    
    cep = request.data.get('cep', '')

    try:
        globo_price = get_price_globo(name, "Drogaria Globo")
    except Exception as e:
        print(f"Failed to find price: {str(e)}")
        globo_price = {'Globo': 0}
    try:
        paguemenos_price = get_price_paguemenos(name, "Pague Menos")
    except Exception as e:
        print(f"Failed to find price: {str(e)}")
        paguemenos_price = {'Pague Menos': 0}
    try:
        drogasil_price = get_drogasil_price(name)
    except Exception as e:
        print(f"Failed to find price: {str(e)}")
        drogasil_price = {'Drogasil': 0}
    try:
        ifood_price = get_ifood_price(name, cep)
    except Exception as e:
        print(f"Failed to find price: {str(e)}")
        ifood_price = {'iFood': 0}

    prices_data = []
    for provider, price in {**ifood_price, **drogasil_price, **globo_price, **paguemenos_price}.items():
        prices_data.append({
            'medicine': medicine.id,
            'provider': provider,
            'price': price
        })
    
    with transaction.atomic():
        for price_data in prices_data:
            existing_price = Price.objects.filter(
                medicine=medicine,
                provider=price_data['provider']
            ).first()
            
            if existing_price:
                serializer = PriceSerializer(existing_price, data=price_data, partial=False)  # Full update
            else:
                serializer = PriceSerializer(data=price_data)
            
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': 'Prices updated successfully'}, status=status.HTTP_200_OK)