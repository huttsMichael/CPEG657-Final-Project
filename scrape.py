import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent
import time
from mongo_utils import initialize_mongodb
from common_utils import read_vehicle_urls_from_csv

def initialize_driver():
    driver = uc.Chrome()
    ua = UserAgent()
    user_agent = ua.random
    options = driver.options
    options.add_argument(f'--user-agent={user_agent}')
    return driver



def extract_vehicle_specs(driver, url, make, model, year, db_update=False):
    print(f"Attempting to load page: {url}")
    vehicle_specs = {'url': url, 'make': make, 'model': model, 'year': year}
    
    if db_update:
        specs_collection, error_collection = initialize_mongodb()

    driver.get(url)

    try:
        # Wait until the specs content is visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".specs-body-content"))
        )
        
        spec_categories = driver.find_elements(By.CSS_SELECTOR, 'div[data-spec="vehicle"]')
        for category in spec_categories:
            items = category.find_elements(By.CSS_SELECTOR, ".css-9dhox.etxmilo0")
            for item in items:
                try:
                    key = item.find_element(By.CSS_SELECTOR, "div:first-child").text.strip(':').strip().replace(" ", "_")
                    value = item.find_element(By.CSS_SELECTOR, "div:last-child").text.strip()
                    vehicle_specs[key] = value
                except NoSuchElementException:
                    print(f"Element not found within the category, skipping this key-value pair.")

        print("Final extracted data:", vehicle_specs)
        if db_update:
            result = specs_collection.update_one({'url': url}, {'$set': vehicle_specs}, upsert=True)
            print(f"Data inserted or updated in MongoDB for {url}, affected documents: {result.modified_count}")

    except TimeoutException as e:
        print(f"Timeout occurred while waiting for page elements: {e}")
        time.sleep(20)
    except NoSuchElementException as e:
        print(f"Failed to find expected elements on the page, review CSS selectors: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def main(db_update=True, recheck=False):
    driver = initialize_driver()
    vehicle_data = read_vehicle_urls_from_csv('vehicle_specs_urls.csv')

    if db_update:
        specs_collection, error_collection = initialize_mongodb()
        processed_urls = set(specs_collection.distinct('url')) | set(error_collection.distinct('url'))
    else:
        processed_urls = set()

    print(f"Loaded {len(vehicle_data)} URLs to process. {len(processed_urls)} URLs are previously processed.")

    try:
        for url, make, model, year in vehicle_data:
            if not recheck and url in processed_urls:
                print(f"Skipping {url} as it has been processed or marked as an error.")
                continue
            extract_vehicle_specs(driver, url, make, model, year, db_update)
            time.sleep(5)  # Throttle requests to avoid being blocked
    finally:
        driver.quit()
        print("Script completed. Quitting driver.")

if __name__ == "__main__":
    main(db_update=True, recheck=False)  # Set db_update and recheck as needed
