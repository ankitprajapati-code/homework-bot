import os
import time
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SCHOOL_USERNAME = os.environ.get("SCHOOL_USERNAME")
SCHOOL_PASSWORD = os.environ.get("SCHOOL_PASSWORD")

LOGIN_URL = "https://gbgs.ac.in/school1/login.php"
HOMEWORK_URL = "https://gbgs.ac.in/school1/p_homeworkold.php"

def send_telegram_photo(photo_path, caption=""):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            requests.post(url, data=data, files=files)

def send_telegram_msg(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)

def take_homework_screenshot():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,1024')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1. Login Page
        driver.get(LOGIN_URL)
        time.sleep(2)

        # 2. Login Details Fill Karein
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys(SCHOOL_USERNAME)
        password_field.send_keys(SCHOOL_PASSWORD)

        try:
            submit_btn = driver.find_element(By.NAME, "submit")
            submit_btn.click()
        except:
            password_field.submit()

        time.sleep(3)

        # 3. Homework Page
        driver.get(HOMEWORK_URL)
        time.sleep(2)

        # 4. 'Show Report' Button Click
        try:
            show_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Show Report')] | //input[@value='Show Report']")
            show_btn.click()
            time.sleep(2)
        except Exception as e:
            print(f"Show report auto-click: {e}")

        # 5. Screenshot Save & Send
        screenshot_path = "homework.png"
        driver.save_screenshot(screenshot_path)

        today_str = datetime.datetime.now().strftime("%d-%b-%Y")
        caption = f"📸 *School Homework ({today_str})*"

        send_telegram_photo(screenshot_path, caption=caption)
        print("Homework screenshot sent successfully!")

    except Exception as e:
        send_telegram_msg(f"⚠️ *Bot Screenshot Error*: {e}")
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    take_homework_screenshot()
