import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_TOKEN = "8613817235:AAEjP-aixzI0NszzZBj9cRlhuTtNNeXAMDA"
CHAT_ID = "5481970935"
BLS_URL = "https://algeria.blsspainvisa.com/algiers/french/appointment.php"
AVAILABLE_KEYWORDS = ["disponible","choisir","créneau","réserver"]
UNAVAILABLE_KEYWORDS = ["aucun rendez-vous","indisponible","complet"]
HEADERS = {"User-Agent":"Mozilla/5.0","Accept-Language":"fr-FR"}
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",json={"chat_id":CHAT_ID,"text":msg,"parse_mode":"HTML"},timeout=15)
    except Exception as e:
        log.error(e)

def check_bls():
    try:
        r = requests.get(BLS_URL,headers=HEADERS,timeout=20)
        soup = BeautifulSoup(r.text,"html.parser")
        text = soup.get_text().lower()
        for kw in UNAVAILABLE_KEYWORDS:
            if kw in text:
                return False
        for kw in AVAILABLE_KEYWORDS:
            if kw in text:
                return True
    except Exception as e:
        log.error(e)
    return False

def main():
    send_telegram("BLS Checker bda yshghel! Sنراقب kol daqiqatayn.")
    count = 0
    while True:
        count += 1
        now = datetime.now().strftime("%H:%M:%S")
        if check_bls():
            send_telegram("MAWID METAH DRWK! " + BLS_URL)
            time.sleep(60)
        else:
            log.info(f"{count} {now} la mawaid")
            if count % 30 == 0:
                send_telegram(f"Bot shaghal - {count} fahsat - la mawaid")
        time.sleep(random.randint(120,240))

if __name__ == "__main__":
    main()
