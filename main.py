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

        # 2. Homework page khol kar form data detect karein
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

        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        today_display = datetime.datetime.now().strftime("%d-%b-%Y")

        for key in list(form_data.keys()):
            if 'date' in key.lower():
                form_data[key] = today_date

        form_data['submit'] = 'Show Report'

        # 3. Report POST request bhejna
        response = session.post(HOMEWORK_URL, data=form_data, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        homework_list = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                cols_text = [c.text.strip() for c in cols]
                
                # Flexible check: agar row me 3 ya usse zyada columns hain
                if len(cols_text) >= 3:
                    if len(cols_text) >= 4:
                        period, subject, classwork, homework = cols_text[:4]
                    else:
                        period, subject, homework = cols_text[:3]
                        classwork = "N/A"
                    
                    # Headers aur empty entries ko filter out karna
                    if "subject" in subject.lower() or "period" in period.lower():
                        continue
                    
                    if homework and "no homework entered" not in homework.lower() and homework != "-":
                        homework_list.append(f"📌 *{subject}* ({period}):\n📖 *CW*: {classwork}\n✏️ *HW*: {homework}")

        if homework_list:
            msg = f"📚 *Aaj Ka Homework ({today_display})*\n\n" + "\n\n".join(homework_list)
            send_telegram_msg(msg)
            print("Homework successfully sent!")
        else:
            send_telegram_msg(f"ℹ️ *{today_display}*: Report aa gayi hai, lekin table me koi active homework text nahi mila.")

    except Exception as e:
        send_telegram_msg(f"⚠️ *Bot Error*: {e}")

if __name__ == "__main__":
    check_homework()
