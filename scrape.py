import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def fetch_vehicle_options_selenium():
    driver = uc.Chrome()

    driver.get("https://www.caranddriver.com/acura/integra/specs")
    print("Website loaded.")

    try:
        print("Locating the 'Research Cars' button...")
        research_cars_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Research Cars')]"))
        )
        print("Found the 'Research Cars' button, attempting to click...")
        research_cars_button.click()
        print("'Research Cars' button clicked.")

        print("Waiting for the 'Vehicle Make' dropdown to appear...")
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "select[aria-label='Vehicle Make']"))
        )
        make_select = driver.find_element(By.CSS_SELECTOR, "select[aria-label='Vehicle Make']")
        print("'Vehicle Make' dropdown is now visible.")
        acura_option = make_select.find_element(By.CSS_SELECTOR, "option[value='acura']")
        acura_option.click()
        print("Acura selected.")

        print("Waiting for the 'Vehicle Model' dropdown to appear...")
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "select[aria-label='Vehicle Model']"))
        )
        model_select = driver.find_element(By.CSS_SELECTOR, "select[aria-label='Vehicle Model']")
        print("'Vehicle Model' dropdown is now visible.")

        model_options = model_select.find_elements(By.TAG_NAME, "option")
        print(f"Total options found in 'Vehicle Model' dropdown: {len(model_options)}")
        for option in model_options:
            print(f"Model Option: {option.text} Value: {option.get_attribute('value')}")

        # Skip the default option and select the first valid model
        for option in model_options:
            if option.get_attribute("value") != "0":  # Assuming "0" is the value for "Select Model"
                print(f"Selecting model: {option.text}")
                option.click()
                print(f"Model '{option.text}' selected.")
                break

    except (NoSuchElementException, TimeoutException) as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

fetch_vehicle_options_selenium()
