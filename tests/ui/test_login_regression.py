from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test_protected_pages_show_login_when_not_authenticated():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        print("\n\nTest 1: Zugriff auf /cars ohne Login")
        driver.get("http://localhost:5173/cars")
        time.sleep(2)

        print("Prüfe: E-Mail-Feld sichtbar")
        email_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter your Email']")
        assert email_field.is_displayed(), "❌ E-Mail-Feld wird nicht angezeigt"

        print("Prüfe: Text 'Sign In' vorhanden")
        assert "Sign In" in driver.page_source, "❌ 'Sign In' nicht im Seiteninhalt gefunden"

        print("Prüfe: 'Sign in'-Button vorhanden")
        sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
        assert sign_in_button.is_displayed(), "❌ 'Sign in'-Button nicht angezeigt"

        print("\n---\nTest 2: Zugriff auf /mybookings ohne Login")
        driver.get("http://localhost:5173/mybookings")
        time.sleep(2)

        print("Prüfe: E-Mail-Feld sichtbar")
        email_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter your Email']")
        assert email_field.is_displayed(), "❌ E-Mail-Feld wird nicht angezeigt"

        print("Prüfe: Text 'Sign In' vorhanden")
        assert "Sign In" in driver.page_source, "❌ 'Sign In' nicht im Seiteninhalt gefunden"

        print("Prüfe: 'Sign in'-Button vorhanden")
        sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
        assert sign_in_button.is_displayed(), "❌ 'Sign in'-Button nicht angezeigt"

    finally:
        driver.quit()
