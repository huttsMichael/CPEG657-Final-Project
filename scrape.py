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
        make_options = make_select.find_elements(By.TAG_NAME, "option")
        for make_option in make_options:
            if make_option.get_attribute("value") and make_option.get_attribute("value") != "0":
                make_option.click()
                print(f"Make '{make_option.text}' selected.")
                break

        print("Waiting for the 'Vehicle Model' dropdown to appear...")
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "select[aria-label='Vehicle Model']"))
        )
        model_select = driver.find_element(By.CSS_SELECTOR, "select[aria-label='Vehicle Model']")
        print("'Vehicle Model' dropdown is now visible.")
        model_options = model_select.find_elements(By.TAG_NAME, "option")
        for model_option in model_options:
            if model_option.get_attribute("value") and model_option.get_attribute("value") != "0":
                model_option.click()
                print(f"Model '{model_option.text}' selected.")
                break

        print("Waiting for the 'Vehicle Year' dropdown to appear...")
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "select[aria-label='Vehicle Year']"))
        )
        year_select = driver.find_element(By.CSS_SELECTOR, "select[aria-label='Vehicle Year']")
        print("'Vehicle Year' dropdown is now visible.")
        year_options = year_select.find_elements(By.TAG_NAME, "option")
        for year_option in year_options:
            if year_option.get_attribute("value") and year_option.get_attribute("value") != "0":
                year_option.click()
                print(f"Year '{year_option.text}' selected.")
                break

    except (NoSuchElementException, TimeoutException) as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

fetch_vehicle_options_selenium()
