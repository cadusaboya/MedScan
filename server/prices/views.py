from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .webscrape import get_ifood_price, get_drogasil_price, get_price_globo, get_price_paguemenos

@api_view(['GET'])
def ifood_view(request, name):
    cep = request.query_params.get('cep', '')
    product_data = get_ifood_price(name, cep)
    
    if product_data is None:
        return Response({"error": "No prices found for the product on iFood"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'name': product_data.get("name"),
        'lowest_price': product_data.get("price")
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def drogasil_view(request, name):
    product_data = get_drogasil_price(name)

    if product_data is None:
        return Response({"error": "No prices found for the product on Drogasil"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'name': product_data.get("name"),
        'lowest_price': product_data.get("price")
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def paguemenos_view(request, name):
    product_data = get_price_paguemenos(name, "Pague Menos")
    
    if product_data is None:
        return Response({"error": "No prices found for the product on Pague Menos"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'name': product_data.get("name"),
        'lowest_price': product_data.get("price")
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def globo_view(request, name):
    product_data = get_price_globo(name, "Drogaria Globo")

    if product_data is None:
        return Response({"error": "No prices found for the product on Drogaria Globo"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'name': product_data.get("name"),
        'lowest_price': product_data.get("price")
    }, status=status.HTTP_200_OK)
