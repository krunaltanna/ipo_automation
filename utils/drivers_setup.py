from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def get_driver(chrome_driver_path):
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)
    return driver
