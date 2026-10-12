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
        'username': SCHOOL_USERNAME,
        'password': SCHOOL_PASSWORD,
        'submit': 'Login'
    }

    try:
        print("Attempting login...")
        login_resp = session.post(LOGIN_URL, data=login_data, headers=headers)
        print(f"Login status code: {login_resp.status_code}")
        
        print("Fetching homework page...")
        response = session.get(HOMEWORK_URL, headers=headers)
        print(f"Homework page status code: {response.status_code}")
        
        # Print page snippet for debugging in GitHub logs
        print("Page Content Snippet:")
        print(response.text[:400])

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if redirected to login page
        if "login" in response.text.lower() and "password" in response.text.lower() and "homework" not in response.text.lower():
            send_telegram_msg("⚠️ *Bot Error*: School website par Login fail ho gaya hai (Session/Form fields mismatch).")
            print("Error: Login failed or redirected back to login page.")
            return

        rows = soup.find_all('tr')
        print(f"Total table rows found: {len(rows)}")
        
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
            print("Telegram message sent successfully!")
        else:
            send_telegram_msg(f"ℹ️ *{today_str}*: Login ho gaya, par table me homework rows match nahi hui.")
            print("No homework rows matched.")

    except Exception as e:
        err_msg = f"Error occurred: {e}"
        print(err_msg)
        send_telegram_msg(f"⚠️ *Bot Error*: {e}")

if __name__ == "__main__":
    check_homework()
