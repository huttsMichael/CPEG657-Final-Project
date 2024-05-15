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
    driver.get(url)
    print(f"Attempting to load page: {url}")
    vehicle_specs = {'url': url, 'make': make, 'model': model, 'year': year}

    if db_update:
        specs_collection, error_collection = initialize_mongodb()

    try:
        if "Access to this page has been denied." in driver.title:
            print("CAPTCHA or access denied detected.")
            if db_update:
                error_collection.insert_one({'url': url, 'error': 'CAPTCHA or access denied'})
            return

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".specs-body-content"))
        )
        spec_categories = driver.find_elements(By.CSS_SELECTOR, 'div[data-spec="vehicle"]')
        for category in spec_categories:
            category_name = category.find_element(By.CSS_SELECTOR, "h3").text
            items = category.find_elements(By.CSS_SELECTOR, ".css-9dhox.etxmilo0")
            category_specs = {}
            for item in items:
                data = item.text.split(':')
                if len(data) == 2:
                    category_specs[data[0].strip()] = data[1].strip()
            print(f"Extracted data for category '{category_name}': {category_specs}")
            vehicle_specs[category_name] = category_specs

        print("Final extracted data:", vehicle_specs)
        if db_update:
            specs_collection.update_one({'url': url}, {'$set': vehicle_specs}, upsert=True)
            print("Data inserted or updated in MongoDB for", url)
    except TimeoutException:
        print(f"Timeout occurred while trying to load specifications from {url}.")
    except NoSuchElementException:
        print(f"Failed to find specification elements on the page {url}.")
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
    main(db_update=False, recheck=True)  # Set db_update and recheck as needed
