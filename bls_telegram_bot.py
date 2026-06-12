import os
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_TOKEN = "8613817235:AAEjP-aixzI0NszzZBj9cRlhuTtNNeXAMDA"
CHAT_ID        = "5481970935"
BLS_URL = "https://algeria.blsspainvisa.com/algiers/french/appointment.php"
AVAILABLE_KEYWORDS   = ["disponible","choisir","sélectionner","créneau","réserver"]
UNAVAILABLE_KEYWORDS = ["aucun rendez-vous","pas de créneau","indisponible","complet"]
MIN_INTERVAL = 120
MAX_INTERVAL = 240
HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Accept-Language":"fr-FR,fr;q=0.9"}
logging.basicConfig(level=logging.INFO,format="%(asctime)s  %(message)s",datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id":CHAT_ID,"text":message,"parse_mode":"HTML"}, timeout=15)
        return r.status_code == 200
    except Exception as e:
        log.error(f"Telegram error: {e}")
        return False

def check_bls():
    try:
        r = requests.get(BLS_URL, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        return False, f"خطأ: {e}"
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(separator=" ").lower()
    for kw in UNAVAILABLE_KEYWORDS:
        if kw in text:
            return False, f"لا مواعيد — «{kw}»"
    for kw in AVAILABLE_KEYWORDS:
        if kw in text:
            return True, f"كلمة «{kw}» موجودة"
    return False, "ما كاين والو واضح"

def main():
    log.info("البوت بدأ!")
    send_telegram("🤖 <b>BLS Checker بدأ يشتغل!</b>\n\nسنراقب موقع BLS كل دقيقتين.\n🔗 " + BLS_URL + "\n\nكي يلقى موعد نبعثلك message فورًا 🔔")
    check_count = 0
    while True:
        check_count += 1
        now = datetime.now().strftime("%H:%M:%S")
        available, reason = check_bls()
        if available:
            log.info(f"🟢 [{check_count}] {now} — {reason}")
            send_telegram(f"🚨 <b>موعد BLS متاح الآن!</b> 🚨\n\n📋 {reason}\n🕐 {now}\n\n👉 <a href='{BLS_URL}'>اضغط هنا وحجز فورًا!</a>\n\n⚡ لا تتأخر!")
            time.sleep(60)
        else:
            log.info(f"🔴 [{check_count}] {now} — {reason}")
            if check_count % 30 == 0:
                send_telegram(f"✅ البوت شاغل — {check_count} فحص\n🕐 {now}\n🔴 لا مواعيد بعد...")
        time.sleep(random.randint(MIN_INTERVAL, MAX_INTERVAL))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        send_telegram("👋 البوت وقف.")
