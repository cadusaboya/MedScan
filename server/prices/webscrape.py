from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse

def get_ifood_price(product_name, cep):
    options = Options()
    options.headless = False  # Set to False to see the browser interactions (helpful for debugging)
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
        time.sleep(2)

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
            cheapest_price = 'No prices found'
    except Exception as e:
        print(f"An error occurred: {e}")
        cheapest_price = 'Failed to retrieve data'
    finally:
        driver.quit()
    
    return cheapest_price

def get_drogasil_price(product_name):
    options = Options()
    options.headless = False  # Set to False to see the browser interactions (helpful for debugging)
    options.add_argument("--incognito")  # Open Chrome in incognito mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Encode spaces in the product name as +
    encoded_product_name = urllib.parse.quote_plus(product_name)
    url = f'https://www.drogasil.com.br/search?w={encoded_product_name}'
    driver.get(url)
    
    # Wait for the page to load (increase sleep time if necessary)
    time.sleep(10)
    
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
            cheapest_price = 'No prices found'
    except Exception as e:
        print(f"An error occurred: {e}")
        cheapest_price = 'Failed to retrieve data'
    finally:
        driver.quit()
    
    return cheapest_price

# Example usage
product_name = 'predsim 40mg'  # Replace with any dynamic product name
cep = 'Belém Pará'  # Replace with the desired CEP 
cheapest_price_ifood = get_ifood_price(product_name, cep)
cheapest_price_drogasil = get_drogasil_price(product_name)
print(f'O preço mais barato de {product_name} em {cep} no Ifood é: R$ {cheapest_price_ifood}\n')
print(f'O preço mais barato de {product_name} na Drogasil é: R$ {cheapest_price_drogasil}')
