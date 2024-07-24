from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse

def get_ifood_prices(product_name):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Encode spaces in the product name as %20
    encoded_product_name = urllib.parse.quote(product_name)
    url = f'https://www.ifood.com.br/busca?q={encoded_product_name}&tab=1'
    driver.get(url)
    
    # Wait for the page to load (increase sleep time if necessary)
    time.sleep(5)  # Increase sleep time if needed
    
    try:
        # Locate product items
        product_elements = driver.find_elements(By.CLASS_NAME, 'merchant-list-carousel__item')  # Update with the correct class name for products
        
        if not product_elements:
            print("No product elements found. Check class names or page structure.")
        
        prices = []
        
        # Split the product_name into keywords
        keywords = product_name.lower().split()
        
        for product_element in product_elements:
            try:
                name_element = product_element.find_element(By.CLASS_NAME, 'merchant-list-carousel__item-title')  # Update with the correct class name for product names
                price_elements = product_element.find_elements(By.CLASS_NAME, 'card-stack-item-price--regular') + \
                                 product_element.find_elements(By.CLASS_NAME, 'card-stack-item-price--promotion')
                
                product_name_text = name_element.text.strip().lower()
                
                # Check if all keywords are present in the product name
                if all(keyword in product_name_text for keyword in keywords):
                    for price_element in price_elements:
                        price_text = price_element.text.strip().replace('R$', '').replace(',', '.').replace('\u00a0', '')
                        print(f"Price Text Found: {price_text}")  # Debugging statement
                        if price_text:  # Ensure the price_text is not empty
                            try:
                                prices.append(float(price_text))
                            except ValueError:
                                print(f"Skipping invalid price: {price_text}")
            except Exception as e:
                print(f"An error occurred while processing product element: {e}")
        
        if prices:
            cheapest_price = min(prices)
        else:
            cheapest_price = 'No prices found'
    except Exception as e:
        print(f"An error occurred: {e}")
        cheapest_price = 'Failed to retrieve data'
    finally:
        driver.quit()
    
    return cheapest_price

# Example usage
product_name = 'Ozempic'  # Replace with any dynamic product name
cheapest_price = get_ifood_prices(product_name)
print(f'The cheapest price for {product_name} is: R$ {cheapest_price}')
