from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import urllib.parse
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import concurrent.futures

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

def get_drogasil_price(product_name):
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    
    # Update the path to your chromedriver if needed
    driver = webdriver.Chrome(service=Service("/Users/cadusaboya/Desktop/coding/MedScan/server/myenv/bin/chromedriver/chromedriver"), options=options)
    
    # Encode spaces in the product name as +
    encoded_product_name = urllib.parse.quote_plus(product_name)
    url = f'https://www.drogasil.com.br/search?w={encoded_product_name}'
    driver.get(url)
    
    try:
        prices = []
        names = []
        urls = []  # List to store URLs
        
        # Split the product_name into keywords
        keywords = product_name.lower().split()
        
        # Locate product items
        product_elements = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-item')))
        
        for product_element in product_elements:
            name_element = product_element.find_element(By.CLASS_NAME, 'product-card-name')
            price_elements = product_element.find_elements(By.CLASS_NAME, 'price-final')
            link_element = product_element.find_element(By.TAG_NAME, 'a')  # Get the link element
            
            product_name_text = name_element.text.strip().lower()
            product_url = link_element.get_attribute('href')  # Get the URL
            
            # Check if all keywords are present in the product name
            if all(keyword in product_name_text for keyword in keywords):
                for price_element in price_elements:
                    price_text = price_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.').replace('\u00a0', '')
                    if price_text:
                        try:
                            prices.append(float(price_text))
                            names.append(name_element.text.strip())
                            urls.append(product_url)  # Store the URL
                            print(f"Drogasil found price: {price_text} for {name_element.text.strip()} at {product_url}")
                        except ValueError:
                            print(f"Skipping invalid price: {price_text}")
        
        if not prices:
            raise ValueError("No prices found for the product")
        
        # Create a list of dictionaries containing all found results
        results = []
        for name, price, url in zip(names, prices, urls):
            results.append({
                "name": name,
                "price": price,
                "url": url
            })
    
    except Exception as e:
        print(f"An error occurred: {e}")
        driver.get_screenshot_as_file("screenshot.png")
        results = []  # Return an empty list in case of an error
    
    finally:
        driver.quit()
    
    return results

def get_price_globo(product_name, company_name):
    if product_name == 'entresto 100mg': 
        product_name = 'entresto 49mg 51mg'
    
    print(f"Searching for {product_name} at {company_name}")
    search_query = f"{product_name} {company_name}"
    response = requests.get(f'https://www.googleapis.com/customsearch/v1?q={search_query}&key={API_KEY}&cx={CX}')
    data = response.json()

    keywords = search_query.lower().split()

    valid_urls = []
    if 'items' in data and len(data['items']) > 0:
        for item in data['items']:
            url = item['link']
            if is_url_valid(url) and url.endswith('/p') and all(keyword in url.lower() for keyword in keywords):
                valid_urls.append(url)
    if not valid_urls:
        print("No valid URLs found.")
        raise ValueError("No prices found for the product")

    prices = []
    names = []
    urls = []  # List to store URLs

    def process_url_globo(url):
        options = Options()
        options.add_argument("--incognito")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(service=Service("/Users/cadusaboya/Desktop/coding/MedScan/server/myenv/bin/chromedriver/chromedriver"), options=options)
        local_prices = []
        local_names = []
        local_urls = []  # Local list to store URLs
        try:
            driver.get(url)
            name_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'vtex-store-components-3-x-productBrand--dagProductName'))
            )
            product_name_text = name_element.text.strip()
            
            price_elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'vtex-product-price-1-x-sellingPriceValue'))
            )
            for price_element in price_elements:
                price_text = price_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.').replace('\u00a0', '')
                if price_text:
                    try:
                        local_prices.append(float(price_text))
                        local_names.append(product_name_text)
                        local_urls.append(url)  # Store the URL associated with the price
                        print(f"Globo found price: {price_text} for {product_name_text}")
                    except ValueError:
                        print(f"Skipping invalid price: {price_text}")
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")
        finally:
            driver.quit()
        return local_prices, local_names, local_urls

    print("Starting to collect Globo prices...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_url_globo, url) for url in valid_urls]
        for future in concurrent.futures.as_completed(futures):
            result_prices, result_names, result_urls = future.result()
            prices.extend(result_prices)
            names.extend(result_names)
            urls.extend(result_urls)

    if not prices:
        raise ValueError("No prices found for the product")
    
    # Create a list of dictionaries containing all found results
    all_results = []
    for name, price, url in zip(names, prices, urls):
        all_results.append({
            "name": name,
            "price": price,
            "url": url
        })

    return all_results

def get_price_paguemenos(product_name, company_name):
    print(f"Searching for {product_name} at {company_name}")
    search_query = f"{product_name} {company_name}"
    # Make the request to the Google Custom Search API
    response = requests.get(f'https://www.googleapis.com/customsearch/v1?q={search_query}&key={API_KEY}&cx={CX}')
    data = response.json()

    # Split the query into keywords
    keywords = search_query.lower().split()

    # Collect all valid URLs
    valid_urls = []
    if 'items' in data and len(data['items']) > 0:
        for item in data['items']:
            url = item['link']
            if is_url_valid(url) and url.endswith('/p') and all(keyword in url for keyword in keywords):
                valid_urls.append(url)

    if not valid_urls:
        print("No valid URLs found.")
        raise ValueError("No prices found for the product")

    print("Starting to collect Pague Menos prices...")
    prices = []
    names = []
    urls = []

    def process_url_paguemenos(url):
        local_prices = []
        local_names = []
        local_urls = []
        options = Options()
        options.add_argument("--incognito")  # Open Chrome in incognito mode
        options.add_argument("--headless")  # Don't open the browser window
        options.add_argument("--disable-gpu")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(service=Service("/Users/cadusaboya/Desktop/coding/MedScan/server/myenv/bin/chromedriver/chromedriver"), options=options)
        try:
            driver.get(url)
            time.sleep(0.1)
            driver.get(url)
            
            try:
                name_element = driver.find_element(By.CLASS_NAME, 'vtex-store-components-3-x-productBrand ')
                product_name_text = name_element.text.strip()
            except:
                name_element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'vtex-store-components-3-x-productBrand '))
                )
                product_name_text = name_element.text.strip()

            try:
                price_elements = driver.find_elements(By.CLASS_NAME, 'vtex-store-components-3-x-currencyContainer')
                if not price_elements:
                    raise ValueError("No price elements found")
            except:
                price_elements = WebDriverWait(driver, 2).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'vtex-store-components-3-x-currencyContainer'))
                )
            for price_element in price_elements:
                price_text = price_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.').replace('\u00a0', '')
                if price_text:
                    try:
                        local_prices.append(float(price_text))
                        local_names.append(product_name_text)
                        local_urls.append(url)
                        print(f"Pague Menos found price: {price_text} for {product_name_text} at {url}")
                    except ValueError:
                        print(f"Skipping invalid price: {price_text}")
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")
        finally:
            driver.quit()
        return local_prices, local_names, local_urls

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_url_paguemenos, url) for url in valid_urls]
        all_results = []
        for future in concurrent.futures.as_completed(futures):
            result_prices, result_names, result_urls = future.result()
            for price, name, url in zip(result_prices, result_names, result_urls):
                all_results.append({
                    "name": name,
                    "price": price,
                    "url": url
                })

    if not all_results:
        raise ValueError("No prices found for the product")

    return all_results
