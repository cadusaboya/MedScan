from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import urllib.parse
import os
from dotenv import load_dotenv

def is_url_valid(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"URL validation error: {e}")
        return False

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
CX = os.getenv('CX')

def get_ifood_price(product_name, cep):
    if product_name == 'Entresto 100mg 60 comprimidos': product_name = 'Entresto 49mg + 51mg 60 comprimidos'
    options = Options()
    options.add_argument("--incognito")  # Open Chrome in incognito mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Encode spaces in the product name as %20
    encoded_product_name = urllib.parse.quote(product_name)
    url = f'https://www.ifood.com.br/busca?q={encoded_product_name}&tab=1'
    driver.get(url)
    
    # Wait for the page to load (increase sleep time if necessary)
    time.sleep(5)
    
    try:
        # Find and click the location button to open the location input (adjust selectors as needed)
        location_button = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/main/div[2]/div/div[2]/button[2]')
        location_button.click()
        time.sleep(2)

        location_button = driver.find_element(By.CLASS_NAME, 'address-search-input__button')
        location_button.click()
        time.sleep(2)
        
        # Input the CEP in the location input field
        location_input = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div/div/div[2]/div/div[1]/div[2]/input')
        location_input.send_keys(cep)
        time.sleep(4)  # Allow time for the input to be processed

        # Find and click the location button to open the location input (adjust selectors as needed)
        location_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div/div/div[2]/div/div[1]/div[3]/ul/li[1]/div/button')
        location_button.click()
        time.sleep(5)

        # Find and click the location button to open the location input (adjust selectors as needed)
        location_button = driver.find_element(By.CLASS_NAME, 'address-maps__submit')
        location_button.click()
        time.sleep(2)

        # Find and click the location button to open the location input (adjust selectors as needed)
        location_input = driver.find_element(By.NAME, 'reference')
        location_input.send_keys(cep)
        time.sleep(2)

                # Find and click the location button to open the location input (adjust selectors as needed)
        location_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div/div/div[3]/div[1]/div[2]/form/div[4]/button')
        location_button.click()
        time.sleep(2)


        
        # Wait for the search results to load
        time.sleep(2)  # Increase sleep time if needed
        
        prices = []
        
        # Split the product_name into keywords
        keywords = product_name.lower().split()
        
        # Locate product items
        product_elements = driver.find_elements(By.CLASS_NAME, 'merchant-list-carousel__item')  # Update with the correct class name for products
        
        for product_element in product_elements:
                name_element = product_element.find_element(By.CLASS_NAME, 'merchant-list-carousel__item-title')  # Update with the correct class name for product names
                price_elements = product_element.find_elements(By.CLASS_NAME, 'card-stack-item-price--regular') + \
                                 product_element.find_elements(By.CLASS_NAME, 'card-stack-item-price--promotion')
                
                product_name_text = name_element.text.strip().lower()
                
                # Check if all keywords are present in the product name
                if all(keyword in product_name_text for keyword in keywords):
                    for price_element in price_elements:
                        price_text = price_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.').replace('\u00a0', '')
                        if price_text:  # Ensure the price_text is not empty
                            try:
                                prices.append(float(price_text))
                            except ValueError:
                                print(f"Skipping invalid price: {price_text}")
        
        if prices:
            cheapest_price = min(prices)
        else:
            raise ValueError("No prices found for the product")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        driver.quit()
    
    return {'iFood': cheapest_price}

def get_drogasil_price(product_name):
    options = Options()
    options.add_argument("--incognito")  # Open Chrome in incognito mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Encode spaces in the product name as +
    encoded_product_name = urllib.parse.quote_plus(product_name)
    url = f'https://www.drogasil.com.br/search?w={encoded_product_name}'
    driver.get(url)
    
    # Wait for the page to load (increase sleep time if necessary)
    time.sleep(15)
    
    try:    
        prices = []
        
        # Split the product_name into keywords
        keywords = product_name.lower().split()
        
        # Locate product items
        product_elements = driver.find_elements(By.CLASS_NAME, 'product-item')  # Update with the correct class name for products
        
        for product_element in product_elements:
                name_element = product_element.find_element(By.CLASS_NAME, 'product-card-name')  # Update with the correct class name for product names
                price_elements = product_element.find_elements(By.CLASS_NAME, 'price-number')
                
                product_name_text = name_element.text.strip().lower()
                
                # Check if all keywords are present in the product name
                if all(keyword in product_name_text for keyword in keywords):
                    for price_element in price_elements:
                        price_text = price_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.').replace('\u00a0', '')
                        if price_text:  # Ensure the price_text is not empty
                            try:
                                prices.append(float(price_text))
                            except ValueError:
                                print(f"Skipping invalid price: {price_text}")
        
        if prices:
            cheapest_price = min(prices)
        else:
            raise ValueError("No prices found for the product")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        driver.quit()
    
    return {'Drogasil': cheapest_price}

def get_price_globo(product_name, company_name):
    if product_name == 'Entresto 100mg 60 comprimidos': product_name = 'Entresto 49mg + 51mg 60 comprimidos'
    options = Options()
    options.add_argument("--incognito")  # Open Chrome in incognito mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    print(f"Searching for {product_name} at {company_name}")
    search_query = f"{product_name} {company_name}"
    # Make the request to the Google Custom Search API
    response = requests.get(f'https://www.googleapis.com/customsearch/v1?q={search_query}&key={API_KEY}&cx={CX}')
    data = response.json()

    # Extract the valid URL from the results
    if 'items' in data and len(data['items']) > 0:
        for item in data['items']:
            url = item['link']
            if is_url_valid(url) and url.endswith('/p'):
                print("Valid URL found:", url)
                break
        else:
            print("No valid URLs found.")
    else:
        print("No results found.")

    driver.get(url)
    
    # Wait for the page to load (increase sleep time if necessary)
    time.sleep(5)
    
    try:
        # Extract the product price from the new page (Update the selector based on the website's structure)
        # Assuming the price can be found with a class name 'price' (adjust as necessary)
        price_elements = driver.find_elements(By.CLASS_NAME, 'vtex-product-price-1-x-sellingPriceValue')  # Example selector
        prices = []
        for price_element in price_elements:
            price_text = price_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.').replace('\u00a0', '')
            if price_text:
                try:
                    prices.append(float(price_text))
                except ValueError:
                    print(f"Skipping invalid price: {price_text}")
        
        if prices:
            cheapest_price = min(prices)
        else:
            raise ValueError("No prices found for the product")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        driver.quit()
    
    return {'Globo': cheapest_price}

def get_price_paguemenos(product_name, company_name):
    options = Options()
    options.add_argument("--incognito")  # Open Chrome in incognito mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    search_query = f"{product_name} {company_name}"
    # Make the request to the Google Custom Search API
    response = requests.get(f'https://www.googleapis.com/customsearch/v1?q={search_query}&key={API_KEY}&cx={CX}')
    data = response.json()

    # Extract the URL of the first result
    if 'items' in data and len(data['items']) > 0:
        first_result_url = data['items'][0]['link']
        print("First result URL:", first_result_url)
    else:
        print("No results found.")
        return 'No results found.'

    url = f"{first_result_url}"
    driver.get(url)
    
    # Wait for the page to load (increase sleep time if necessary)
    time.sleep(5)
    
    try:
        # Extract the product price from the new page (Update the selector based on the website's structure)
        # Assuming the price can be found with a class name 'price' (adjust as necessary)
        price_elements = driver.find_elements(By.CLASS_NAME, 'vtex-store-components-3-x-currencyContainer')  # Example selector
        prices = []
        for price_element in price_elements:
            price_text = price_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.').replace('\u00a0', '')
            if price_text:
                try:
                    prices.append(float(price_text))
                except ValueError:
                    print(f"Skipping invalid price: {price_text}")
        
        if prices:
            cheapest_price = min(prices)
        else:
            raise ValueError("No prices found for the product")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        driver.quit()
    
    
    return {'Pague Menos': cheapest_price}