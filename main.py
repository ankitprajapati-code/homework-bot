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

        # 2. Homework page khol kar form ke saare fields detect karein
        hw_page = session.get(HOMEWORK_URL, headers=headers)
        soup_page = BeautifulSoup(hw_page.text, 'html.parser')

        form_data = {}
        form = soup_page.find('form')
        if form:
            for inp in form.find_all(['input', 'select']):
                name = inp.get('name')
                if not name:
                    continue
                val = inp.get('value', '')
                if inp.name == 'select':
                    opt = inp.find('option')
                    if opt and opt.get('value'):
                        val = opt.get('value')
                form_data[name] = val

        # Aaj ki date aur report submit button set karna
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        today_display = datetime.datetime.now().strftime("%d-%b-%Y")

        for key in list(form_data.keys()):
            k_lower = key.lower()
            if 'date' in k_lower:
                form_data[key] = today_date

        form_data['submit'] = 'Show Report'

        # 3. Report form POST request bhej kar data load karein
        response = session.post(HOMEWORK_URL, data=form_data, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        homework_list = []
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                cols_text = [c.text.strip() for c in cols]
                
                if len(cols_text) >= 4:
                    period, subject, classwork, homework = cols_text[:4]
                    if homework and "No homework entered" not in homework and "homework" not in homework.lower() and "subject" not in subject.lower() and "period" not in period.lower():
                        homework_list.append(f"📌 *{subject}* ({period}):\n📖 *CW*: {classwork}\n✏️ *HW*: {homework}")

        if homework_list:
            msg = f"📚 *Aaj Ka Homework ({today_display})*\n\n" + "\n\n".join(homework_list)
            send_telegram_msg(msg)
            print("Homework sent successfully!")
        else:
            send_telegram_msg(f"ℹ️ *{today_display}*: Report generate ho gayi, par table me homework rows read nahi ho payi.")

    except Exception as e:
        send_telegram_msg(f"⚠️ *Bot Error*: {e}")

if __name__ == "__main__":
    check_homework()
