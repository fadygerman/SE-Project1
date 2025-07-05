import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    """Create a Chrome WebDriver instance for testing."""
    # Configure Chrome options for better compatibility with Chromium
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    local_chromedriver = os.path.join(os.path.dirname(__file__), "chromedriver")
    service = Service(executable_path=local_chromedriver)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    yield driver
    
    # Teardown - close the browser after the test
    driver.quit()

