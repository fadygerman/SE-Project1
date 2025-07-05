from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def test_return_car():
    driver = webdriver.Chrome()

    # App öffnen und Login durchführen
    driver.get("http://localhost:5173")
    driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]").click()
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys("nils_petsch@gmx.at")
    driver.find_element(By.NAME, "password").send_keys("Test123#")
    driver.find_element(By.CLASS_NAME, "amplify-button--primary").click()
    time.sleep(3)

    # Direkt zu My Bookings
    driver.get("http://localhost:5173/mybookings")
    time.sleep(2)

    # „View Details“ klicken
    driver.find_element(By.LINK_TEXT, "View Details").click()
    time.sleep(2)

    # Warten und dann „Return Car“ klicken (falls vorhanden)
    try:
        driver.find_element(By.XPATH, '//button[text()="Return Car"]').click()
        time.sleep(1)
    except:
        pass  # Falls Button nicht da ist, einfach weiter (z. B. wenn schon returned)

    # Prüfen, ob ein Status-Feld „COMPLETED“ enthält
    completed_elements = driver.find_elements(By.XPATH, '//dd[contains(text(),"COMPLETED")]')
    
    assert len(completed_elements) > 0, "Kein Booking mit Status COMPLETED gefunden."

    driver.quit()
