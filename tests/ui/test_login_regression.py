from selenium import webdriver
from selenium.webdriver.common.by import By

def test_access_protected_page_with_invalid_token():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5173")

    driver.execute_script("localStorage.setItem('access_token', 'xyz123_invalid');")
    driver.get("http://localhost:5173/mybookings")

    assert "Willkommen" in driver.page_source  
    driver.quit()
