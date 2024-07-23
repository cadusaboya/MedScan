# prices/serializers.py

from rest_framework import serializers
from .models import Medicine, Price

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['id', 'provider', 'price', 'medicine']

class MedicineSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True, read_only=True)

    class Meta:
        model = Medicine
        fields = ['id', 'name', 'prices']