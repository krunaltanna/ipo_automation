import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from utils.drivers_setup import get_driver
from utils.emails_utils import fetch_otp
from utils.data_loader import load_ipo_data, get_client_details, load_client_master_details
import csv
import constant
import time
from concurrent.futures import ThreadPoolExecutor

CHROME_DRIVER_PATH = constant.CHROME_DRIVER_PATH
BANKING_WEBSITE_URL = constant.BANKING_WEBSITE_URL



# Parametrize the test to run with different CSV data
def wait_for_element(driver, by, value, timeout=15, retries=3, retry_interval=2):
    """
    Wait for an element to be visible with retries.
    
    Parameters:
    - driver: WebDriver instance
    - by: Locator strategy (e.g., By.ID, By.XPATH)
    - value: Locator value
    - timeout: Time to wait for the element in each attempt (default 15 seconds)
    - retries: Number of retry attempts (default 3)
    - retry_interval: Time to wait between retries (default 5 seconds)
    
    Returns:
    - WebElement if found.
    - Raises TimeoutException if the element is not found after all retries.
    """
    attempt = 0
    while attempt < retries:
        try:
            # Try to locate the element
            return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
        except TimeoutException:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)  # Wait before retrying

    # If the element is not found after retries, raise an exception
    raise TimeoutException(f"Element located by {by}='{value}' not found after {retries} retries.")

def switch_to_frame(frame_name, driver, timeout):
    WebDriverWait(driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, frame_name))
        )

def test_ipo_flow(data, client_details):
    """Test case to apply IPO flow with given data."""
    # Setup Chrome options for each test run
    
    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    client_data = get_client_details(data['client_id'], client_details)

    driver.get(BANKING_WEBSITE_URL) 

    # Step 1: Login
    wait_for_element(driver, By.ID, 'userName').send_keys(client_data['client_username'])
    wait_for_element(driver, By.ID, 'credentialInputField').send_keys(client_data['client_password'])
    wait_for_element(driver, By.XPATH, "//button[@type='submit']").click()

    # Step 2: Fetch OTP from email
    otp = fetch_otp(client_data['client_email'], client_data['client_email_app_password'])
    wait_for_element(driver, By.ID, 'otpMobile').send_keys(otp)
    wait_for_element(driver, By.XPATH, "//button[contains(text(), 'Secure login')]").click()

    print("OTP Entered Successfully")

    # Step 3: Navigate to Investments > IPO
    wait_for_element(driver, By.XPATH, "//span[text()='Investments']").click()
    wait_for_element(driver, By.XPATH, "//p[text()='IPO (ASBA)']").click()

    # Step 4: Apply Now

    frame_name = "knb2ContainerFrame"
    switch_to_frame(frame_name, driver, 15)

    frame_name = "appmenu"
    switch_to_frame(frame_name, driver, 15)
    
    wait_for_element(driver, By.XPATH, "//a[text()='Transaction']/ancestor::li/descendant::li/a[@href='javascript:void()' and @onclick='applyNow()' and text()='Apply Now ']").click()

    driver.switch_to.default_content()

    frame_name = "knb2ContainerFrame"
    switch_to_frame(frame_name, driver, 15)

    frame_name = "contentmenu"
    switch_to_frame(frame_name, driver, 15)

    # Step 5: Select Beneficiary and Company
    wait_for_element(driver, By.ID, "selBeneficiary").click()
    wait_for_element(driver, By.XPATH, f"//option[contains(text(), 'AC:XX')]").click()

    wait_for_element(driver, By.ID, "selCompany").click()
    wait_for_element(driver, By.XPATH, f"//option[contains(text(), '{data['script']}')]").click()

    # Handle Alerts if any
    try:
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert.accept()
    except:
        pass

    wait_for_element(driver, By.XPATH, f"//select[@id='invCat']").click()
    wait_for_element(driver, By.XPATH, f"//select[@id='invCat']/option[contains(text(), '{data['quota']}')]").click()
    
    wait_for_element(driver, By.XPATH, f"//a[text()='Next']").click()

    #Fetch the total bid size:

    text_element = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, "//td[span[@class='bold' and text()='Min. No. of Shares']]/following-sibling::td/span[@class='small']"))
    )

    bid_size = text_element.text

    input_element = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@id='txtSharesIdIPO0']"))
    )

    # Type the text into the input element
    input_element.clear()  # Clear any pre-filled text
    input_element.send_keys(bid_size)

    #wait_for_element(driver, By.XPATH, f"//select[@id='cutoffIdIPO0']").click()

    wait_for_element(driver, By.XPATH, f"//input[@id='checkTncId']").click()    
    
    wait_for_element(driver, By.XPATH, f"//a[text()='Next']").click()

    wait_for_element(driver, By.ID, "Confirm_Submit_Id").click()

    print("IPO Bid Successfully!")
   

    

# Main logic to iterate over CSV rows
if __name__ == "__main__":
    # Load test data from CSV
    ipo_data = load_ipo_data("data/apply_data/ipo_details_02_01_25.csv")
    client_details = load_client_master_details("data/client_master_details.csv")

    # Iterate over each row in the data and run the test for each row
    for data in ipo_data:
        print(f"Running test for: {data['client_id']} with company {data['script']}")
        test_ipo_flow(data, client_details)

    #  # Create a ThreadPoolExecutor to run tests in parallel
    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     # Run test_ipo_flow for each row in parallel
    #     executor.map(test_ipo_flow, test_data)