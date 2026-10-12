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

    try:
        # 1. Login page pehle GET karke dekhte hain
        login_page = session.get(LOGIN_URL, headers=headers)
        soup_login = BeautifulSoup(login_page.text, 'html.parser')
        
        # Form inputs dhoondhte hain
        inputs = soup_login.find_all('input')
        input_names = [inp.get('name') for inp in inputs if inp.get('name')]
        print(f"Login form input names found on website: {input_names}")

        # Web form fields try karte hain
        login_data = {}
        for inp_name in input_names:
            name_lower = inp_name.lower()
            if 'user' in name_lower or 'admin' in name_lower or 'id' in name_lower or 'login' in name_lower or 'roll' in name_lower:
                login_data[inp_name] = SCHOOL_USERNAME
            elif 'pass' in name_lower or 'pwd' in name_lower:
                login_data[inp_name] = SCHOOL_PASSWORD
            elif 'sub' in name_lower or 'btn' in name_lower or 'log' in name_lower:
                login_data[inp_name] = 'Login'

        # Fallback agar names nahi mile
        if not login_data:
            login_data = {'username': SCHOOL_USERNAME, 'password': SCHOOL_PASSWORD, 'submit': 'Login'}

        print(f"Submitting payload with keys: {list(login_data.keys())}")
        login_resp = session.post(LOGIN_URL, data=login_data, headers=headers)

        # 2. Homework page fetch karein
        response = session.get(HOMEWORK_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        if "login" in response.text.lower() and "password" in response.text.lower() and "homework" not in response.text.lower():
            send_telegram_msg(f"⚠️ *Bot Error*: School website par Login fail ho gaya.\nForm fields detect huye the: `{input_names}`")
            return

        rows = soup.find_all('tr')
        homework_list = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols_text = [c.text.strip() for c in cols]
            
            if len(cols_text) >= 4:
                period, subject, classwork, homework = cols_text[:4]
                if homework and "No homework entered" not in homework and "Homework" not in homework:
                    homework_list.append(f"📌 *{subject}* ({period}):\n📖 Classwork: {classwork}\n✏️ Homework: {homework}")

        today_str = datetime.datetime.now().strftime("%d-%b-%Y")

        if homework_list:
            msg = f"📚 *Aaj Ka Homework ({today_str})*\n\n" + "\n\n".join(homework_list)
            send_telegram_msg(msg)
        else:
            send_telegram_msg(f"ℹ️ *{today_str}*: Login ho gaya hai, par website par abhi homework update nahi hua hai.")

    except Exception as e:
        send_telegram_msg(f"⚠️ *Bot Error*: {e}")

if __name__ == "__main__":
    check_homework()
