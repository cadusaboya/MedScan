import csv
import requests
import urllib.parse
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import medicines from a CSV file'
    
    def handle(self, *args, **kwargs):
        with open('prices/data/medicines.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                medicine_name = row['medicine_name']
                print(f"Adding prices for {medicine_name}...")
                
                # Encode the medicine name for the URL
                encoded_medicine_name = urllib.parse.quote(medicine_name)
                
                # Send a POST request to your add_price_to_medicine view
                response = requests.put(
                    f'http://localhost:8000/api/medicines/{encoded_medicine_name}/prices/add/',
                    json={'cep': 'Belém Pará'}  # Replace with the desired CEP if necessary
                )
                
                if response.status_code == 201:
                    print(f"Successfully added prices for {medicine_name}")
                else:
                    print(f"Failed to add prices for {medicine_name}: {response.content.decode()}")