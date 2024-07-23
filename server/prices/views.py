# prices/views.py

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Medicine, Price
from .serializers import MedicineSerializer, PriceSerializer

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
    
    # Prepare the data for the PriceSerializer
    data = request.data
    data['medicine'] = medicine.id
    print(data)

    serializer = PriceSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)