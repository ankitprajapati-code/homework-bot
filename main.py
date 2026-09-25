import os
import requests
from bs4 import BeautifulSoup
import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SCHOOL_URL = "https://gbgs.ac.in/school1/p_homeworkold.php"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

def check_homework():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(SCHOOL_URL, headers=headers)
        if response.status_code != 200:
            print("Website load nahi ho saki.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
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
            print("Telegram message sent successfully!")
        else:
            send_telegram_msg(f"ℹ️ *{today_str}*: Aaj school website par abhi koi naya homework update nahi hua hai.")
            print("No homework uploaded.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    check_homework()
