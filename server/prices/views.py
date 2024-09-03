from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .webscrape import get_drogasil_price, get_price_globo, get_price_paguemenos
    
@api_view(['GET'])
def drogasil_view(request, name):
    # Assuming get_price_paguemenos returns a list of dictionaries with name, price, and url
    product_data_list = get_drogasil_price(name)
    
    if not product_data_list:
        return Response({"error": "No prices found for the product on Drogasil"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(product_data_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def paguemenos_view(request, name):
    # Assuming get_price_paguemenos returns a list of dictionaries with name, price, and url
    product_data_list = get_price_paguemenos(name, "Pague Menos")
    
    if not product_data_list:
        return Response({"error": "No prices found for the product on Pague Menos"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(product_data_list, status=status.HTTP_200_OK)

@api_view(['GET'])
def globo_view(request, name):
    # Assuming get_price_paguemenos returns a list of dictionaries with name, price, and url
    product_data_list = get_price_globo(name, "Drogaria Globo")
    
    if not product_data_list:
        return Response({"error": "No prices found for the product on Drogaria Globo"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(product_data_list, status=status.HTTP_200_OK)
