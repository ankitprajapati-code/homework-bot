import os
import requests
from bs4 import BeautifulSoup
import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SCHOOL_USERNAME = os.environ.get("SCHOOL_USERNAME")
SCHOOL_PASSWORD = os.environ.get("SCHOOL_PASSWORD")

LOGIN_URL = "https://gbgs.ac.in/school1/login.php"
HOMEWORK_URL = "https://gbgs.ac.in/school1/p_homeworkold.php"

def send_telegram_msg(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)

def check_homework():
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    login_data = {
        'user_type': 'student',
        'username': SCHOOL_USERNAME,
        'password': SCHOOL_PASSWORD,
        'submit': 'Login',
        'login': 'Login'
    }

    try:
        # 1. Login session start karein
        session.get(LOGIN_URL, headers=headers)
        session.post(LOGIN_URL, data=login_data, headers=headers)

        # 2. Homework page par GET request bhej kar form parameters trace karein
        hw_page = session.get(HOMEWORK_URL, headers=headers)
        soup_page = BeautifulSoup(hw_page.text, 'html.parser')

        today_date = datetime.datetime.now().strftime("%Y-%m-%d") # Format YYYY-MM-DD ya DD/MM/YYYY
        today_display = datetime.datetime.now().strftime("%d-%b-%Y")

        # Student selection aur Show Report ke liye payload
        # Agar student dropdown input me koi specific ID hai toh parse karein
        student_option = soup_page.find('option')
        student_val = student_option.get('value') if student_option else ''

        report_payload = {
            'student_id': student_val,
            'search_date': today_date,
            'date': datetime.datetime.now().strftime("%d/%m/%Y"),
            'submit': 'Show Report',
            'search': 'Show Report'
        }

        # POST request to submit 'Show Report'
        response = session.post(HOMEWORK_URL, data=report_payload, headers=headers)
        
        # Fallback agar GET response me hi data mil jaye
        if "INFORMATION TECHNOLOGY" not in response.text and "ENGLISH" not in response.text:
            response = hw_page

        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.find_all('tr')
        homework_list = []
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols_text = [c.text.strip() for c in cols]
            
            # Period, Subject, Classwork, Homework columns
            if len(cols_text) >= 4:
                period, subject, classwork, homework = cols_text[:4]
                
                # Header row aur empty homework filter out karein
                if homework and "No homework entered" not in homework and "homework" not in homework.lower() and "period" not in period.lower():
                    homework_list.append(f"📌 *{subject}* ({period}):\n📖 *Classwork*: {classwork}\n✏️ *Homework*: {homework}")

        if homework_list:
            msg = f"📚 *Aaj Ka Homework ({today_display})*\n\n" + "\n\n".join(homework_list)
            send_telegram_msg(msg)
            print("Homework sent successfully!")
        else:
            send_telegram_msg(f"ℹ️ *{today_display}*: Website connect ho gayi par homework rows match nahi hui.")

    except Exception as e:
        send_telegram_msg(f"⚠️ *Bot Error*: {e}")

if __name__ == "__main__":
    check_homework()
