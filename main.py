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
        # 1. Login Page Kholein
        driver.get(LOGIN_URL)
        time.sleep(3)

        # 2. Parent/Student Role Tab Click Karein (agar zaroori ho)
        try:
            parent_tab = driver.find_element(By.XPATH, "//*[contains(text(), 'Parent') or contains(text(), 'Student')]")
            parent_tab.click()
            time.sleep(1)
        except:
            pass

        # 3. Username aur Password Bharein
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.clear()
        username_field.send_keys(SCHOOL_USERNAME)
        password_field.clear()
        password_field.send_keys(SCHOOL_PASSWORD)

        # 4. 'SECURE LOGIN' Button Click Karein
        try:
            secure_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'SECURE LOGIN')] | //button[@type='submit']")
            secure_btn.click()
        except:
            password_field.submit()

        # Login hone ke liye thoda wait karein
        time.sleep(5)

        # 5. Homework Page Par Jayein
        driver.get(HOMEWORK_URL)
        time.sleep(3)

        # 6. 'Show Report' Button Click Karein
        try:
            show_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Show Report')] | //input[@value='Show Report']")
            show_btn.click()
            time.sleep(3)
        except Exception as e:
            print(f"Show report click notice: {e}")

        # 7. Screenshot Save & Send Karein
        screenshot_path = "homework.png"
        driver.save_screenshot(screenshot_path)

        today_str = datetime.datetime.now().strftime("%d-%b-%Y")
        caption = f"📸 *School Homework ({today_str})*"

        send_telegram_photo(screenshot_path, caption=caption)
        print("Homework screenshot sent successfully!")

    except Exception as e:
        send_telegram_msg(f"⚠️ *Bot Error*: {e}")
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    take_homework_screenshot()
