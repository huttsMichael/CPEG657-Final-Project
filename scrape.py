import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent
import time
import csv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def initialize_driver():
    driver = uc.Chrome()
    ua = UserAgent()
    user_agent = ua.random
    options = driver.options
    options.add_argument(f'--user-agent={user_agent}')

    return driver

def initialize_mongodb():
    uri = ""
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['vehicle_data']
    collection = db['specs']
    return collection

def collect_vehicle_urls(driver):
    driver.get("https://www.caranddriver.com/acura/integra/specs")
    print("Website loaded.")

    completed_makes = set()
    vehicle_urls = []

    # Check if the CSV already exists and read the last make processed
    csv_filename = 'vehicle_specs_urls.csv'
    if os.path.exists(csv_filename):
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                completed_makes.add(row[0])

    try:
        print("Locating the 'Research Cars' button...")
        research_cars_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Research Cars')]"))
        )
        research_cars_button.click()
        print("'Research Cars' button clicked.")

        print("Waiting for the 'Vehicle Make' dropdown to appear...")
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "select[aria-label='Vehicle Make']"))
        )
        make_select = driver.find_element(By.CSS_SELECTOR, "select[aria-label='Vehicle Make']")
        makes = [(option.text, option.get_attribute("value")) for option in make_select.find_elements(By.TAG_NAME, "option") if option.get_attribute("value") != "0"]

        for make_name, make_value in makes:
            if make_name in completed_makes:
                print(f"Skipping completed make: {make_name}")
                continue
            print(f"Preparing to select make: {make_name}")
            # Find and click the option again to avoid stale reference
            make_option = make_select.find_element(By.CSS_SELECTOR, f"option[value='{make_value}']")
            make_option.click()
            print(f"Make '{make_name}' selected.")

            time.sleep(1)  # Allow time for the model dropdown to update

            model_select = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "select[aria-label='Vehicle Model']"))
            )
            models = [(option.text, option.get_attribute("value")) for option in model_select.find_elements(By.TAG_NAME, "option") if option.get_attribute("value") != "0"]

            for model_name, model_value in models:
                model_option = model_select.find_element(By.CSS_SELECTOR, f"option[value='{model_value}']")
                model_option.click()
                print(f"Model '{model_name}' selected.")

                time.sleep(1)

                year_select = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "select[aria-label='Vehicle Year']"))
                )
                time.sleep(0.1)

                years = [option.text for option in year_select.find_elements(By.TAG_NAME, "option") if option.get_attribute("value") != "0"]

                for year in years:
                    print(f"Year '{year}' selected with Make '{make_name}' and Model '{model_name}'.")

                # Correctly format the model name for URL (replace spaces with dashes)
                model_value_url = model_value.replace(" ", "-").lower()
                url = f"https://www.caranddriver.com/{make_value}/{model_value_url}/specs"
                vehicle_urls.append([make_name, model_name, year, url])
                print(f"URL generated: {url}")

    except (NoSuchElementException, TimeoutException) as e:
        print("An error occurred:", e)
    finally:
        # Append data to a CSV file
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not completed_makes:  # Write header only if the file was newly created
                writer.writerow(['Make', 'Model', 'Year', 'URL'])
            writer.writerows(vehicle_urls)
        print(f"Data has been written to '{csv_filename}'")
        # driver.quit()
        return vehicle_urls

def extract_vehicle_specs(driver, url, collection):
    driver.get(url)
    print(f"Attempting to load page: {url}")
    vehicle_specs = {'url': url}

    try:
        error_check = driver.find_elements(By.CSS_SELECTOR, "h2.css-1emyy0d")
        if error_check and "Oops! We don't have the page you're looking for." in error_check[0].text:
            print(f"404 Error Page Detected at {url}. Skipping...")
            return None
    except Exception as e:
        print(f"Error checking for 404: {e}")

    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".specs-body-content"))
        )
        spec_categories = driver.find_elements(By.CSS_SELECTOR, 'div[data-spec="vehicle"]')
        print(f"Found {len(spec_categories)} specification categories.")

        for category in spec_categories:
            category_name = category.find_element(By.CSS_SELECTOR, "h3").text
            items = category.find_elements(By.CSS_SELECTOR, ".css-9dhox.etxmilo0")
            for item in items:
                data = item.text.split(':')
                if len(data) == 2:
                    vehicle_specs[data[0].strip()] = data[1].strip()
            print(f"Extracted data for category: {category_name}")

        collection.insert_one(vehicle_specs)
        print("Data inserted into MongoDB for", url)
    except TimeoutException:
        print(f"Timeout occurred while trying to load specifications from {url}. Adding delay before next request.")
        time.sleep(60)  # Delay for 60 seconds before next request
    except NoSuchElementException:
        print(f"Failed to find specification elements on the page {url}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def read_vehicle_urls_from_csv(file_path):
    urls = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            urls.append(row['URL'])
    return urls

def main():
    driver = initialize_driver()
    collection = initialize_mongodb()
    csv_file = 'vehicle_specs_urls.csv'
    if not os.path.exists(csv_file):
        print("No URL CSV file found. Please ensure your URL list is available.")
        return

    urls = read_vehicle_urls_from_csv(csv_file)
    print(f"Loaded {len(urls)} URLs to process.")

    try:
        for url in urls:
            extract_vehicle_specs(driver, url, collection)
            time.sleep(2)  # General delay between requests to prevent rate limiting
    finally:
        print("hit final finally, quitting cleanly")
        driver.quit()

if __name__ == "__main__":
    main()