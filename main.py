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

        # 2. Homework page fetch karein
        response = session.get(HOMEWORK_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        homework_list = []
        
        # Website par jitni bhi tables hain sabhi ko check karenge
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                cols_text = [c.text.strip() for c in cols]
                
                # Agar row me kam se kam 4 columns hain (Period, Subject, Classwork, Homework)
                if len(cols_text) >= 4:
                    period, subject, classwork, homework = cols_text[:4]
                    
                    # Header titles ya empty entries ko chhod kar baki sab add karenge
                    if homework and "No homework entered" not in homework and "homework" not in homework.lower() and "subject" not in subject.lower():
                        homework_list.append(f"📌 *{subject}* ({period}):\n📖 *CW*: {classwork}\n✏️ *HW*: {homework}")

        today_display = datetime.datetime.now().strftime("%d-%b-%Y")

        if homework_list:
            msg = f"📚 *Aaj Ka Homework ({today_display})*\n\n" + "\n\n".join(homework_list)
            send_telegram_msg(msg)
            print("Homework successfully sent!")
        else:
            send_telegram_msg(f"ℹ️ *{today_display}*: Login successful hai, par table me koi active homework entries nahi mili.")

    except Exception as e:
        send_telegram_msg(f"⚠️ *Bot Error*: {e}")

if __name__ == "__main__":
    check_homework()
