from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test_access_mybookings_without_login():
    options = Options()
    options.add_argument('--headless') 
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("http://localhost:5173/mybookings")
        time.sleep(2) 

        assert "Willkommen" in driver.page_source or "Login" in driver.page_source

        assert "/landing" in driver.current_url or "/" == driver.current_url

    finally:
        driver.quit()
