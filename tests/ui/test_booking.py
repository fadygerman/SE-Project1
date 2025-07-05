from datetime import datetime
from decimal import Decimal
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pytest

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, backend_path)

from db_seed import init_db, seed_data

def reset_db():
  init_db()
  seed_data()

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
    
    driver = webdriver.Chrome(options=chrome_options)
    
    yield driver
    
    # Teardown - close the browser after the test
    driver.quit()

def test_create_booking(driver):
  """Test the complete booking flow from login to booking creation.
  Preconditions:
    - chromedriver is present in the current directory
      - https://googlechromelabs.github.io/chrome-for-testing/#stable
    - currency converter is running
    - database is running
    - backend is running
    - frontend is running
  
  """
  # TODO: implement the function
  reset_db()

  driver.get("http://localhost:5173/")

  login(driver, "szulcalbert.work@gmail.com", "h;@4_2uhWP44tC#")
  time.sleep(3)

  select_car(driver, 1)
  time.sleep(2)

  price_per_day = get_price_from_div(driver)

  select_start_date(driver)
  time.sleep(1)

  click_outside_calendar(driver)
  time.sleep(1)

  select_end_date(driver)
  time.sleep(1)

  click_outside_calendar(driver)
  time.sleep(1)

  book_now(driver)
  time.sleep(2)

  assert "Car booked from" in get_alert_text(driver)
  

  driver.get("http://localhost:5173/mybookings")
  time.sleep(2)
  
  booking_price = get_booking_price(driver)
  
  assert booking_price == price_per_day # we booked just one day
  time.sleep(1)


def login(driver, email, password):
  # Find the email input field and enter an email address
  email_input = driver.find_element(By.NAME, "username")
  email_input.send_keys(email)

  # Find the password input field and enter a password
  password_input = driver.find_element(By.NAME, "password")
  password_input.send_keys(password)

  # Find the login button and click it
  login_button = driver.find_element(By.XPATH, "//button[contains(@class, 'amplify-button--primary') and contains(text(), 'Sign in')]")
  login_button.click()
  
def select_car(driver, car_id):
  book_now_button = driver.find_element(By.XPATH, f"//a[contains(@href, '/cars/{car_id}') and contains(@class, 'text-blue-500') and contains(text(), 'Book Now')]")
  book_now_button.click()

def select_start_date(driver):
    # Find and click the Select start date button
  from_date_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Select start date')]")
  from_date_button.click()

  # Wait for calendar to load
  time.sleep(2)

  # click next month
  next_month_button = driver.find_element(By.XPATH, "//button[contains(@name, 'next-month')]")
  next_month_button.click()

  # Click on first day of a month
  first_day_of_a_month = driver.find_element(By.XPATH, "//button[@name='day' and text()='1' and not(contains(@class, 'day-outside'))]")
  first_day_of_a_month.click()

def select_end_date(driver):
   # Find and click the Select end date button
  end_date_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Select end date')]")
  end_date_button.click()

  time.sleep(1)

  # click next month
  next_month_button = driver.find_element(By.XPATH, "//button[contains(@name, 'next-month')]")
  next_month_button.click()

  time.sleep(1)

  # click on first day of a month
  first_day_of_a_month = driver.find_element(By.XPATH, "//button[@name='day' and text()='1' and not(contains(@class, 'day-outside'))]")
  first_day_of_a_month.click()

def book_now(driver):
  book_now_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Book Now')]")
  book_now_button.click()

def get_alert_text(driver) -> str:
  try:
    alert = driver.switch_to.alert
    popup_text = alert.text
    print(f"Alert text: {popup_text}")
    alert.accept()  # Click OK, or use alert.dismiss() to cancel
    return popup_text
  except:
    print("No browser alert found")
    return ""

def click_outside_calendar(driver):
  driver.find_element(By.TAG_NAME, "body").click()

def get_price_from_div(driver) -> Decimal:
  """Extract the price number from the price div"""
  try:
    # Find the div containing the price information
    price_dd = driver.find_element(By.XPATH, "//dt[contains(text(), 'Price')]/following-sibling::dd")
    
    # Get the text content and extract the numeric part
    price_text = price_dd.text.split()[0]  # Get first part before any spaces (like "45.00")
    return Decimal(price_text)
    
  except Exception as e:
    print(f"Error extracting price: {e}")
    return Decimal(0)
  
def get_booking_price(driver) -> Decimal:
  total_cost_div = driver.find_element(By.XPATH, "//span[contains(text(), 'Total Cost:')]/following-sibling::span")
  price_text = total_cost_div.text.replace('$', '')  # Remove dollar sign
  return Decimal(price_text)