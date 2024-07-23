# prices/models.py

from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Price(models.Model):
    medicine = models.ForeignKey(Medicine, related_name='prices', on_delete=models.CASCADE)
    provider = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.provider}: R$ {self.price}"