import os
import time
import threading
import requests
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION (Pulled from Render Environment Variables) ---
TELEGRAM_TOKEN = os.getenv('TG_TOKEN')
CHAT_ID = os.getenv('TG_CHAT_ID')
NOON_COOKIE = os.getenv('NOON_COOKIE')

def notify(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials missing!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Notification Error: {e}")

def check_noon_slots():
    print(f"🚀 Monitor Started at {datetime.now()}")
    
    url = 'https://fbn.noon.partners/_svc/inbound-scheduler/day/fbn/v1/capacity'
    
    # Headers exactly as you provided in your cURL
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'cookie': NOON_COOKIE,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-locale': 'en-eg',
        'x-project': 'PRJ452348',
        'origin': 'https://fbn.noon.partners',
        'referer': 'https://fbn.noon.partners/en-eg/asn/schedule/A05094139PN?project=PRJ452348'
    }

    payload = {
        "asn_nr": "A05094139PN",
        "id_partner": 452348,
        "total_units": 949,
        "warehouse_to": "CAI04",
        "id_value": "3456"
    }

    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking Noon Egypt (CAI04)...")
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                notify(f"Response Received {result}")
                # Noon usually returns a list []. If it has items, a slot is open.
                if isinstance(result, list) and len(result) > 0:
                    notify("🔥 NOON SLOT AVAILABLE! Go to the Seller Lab immediately!")
                    notify(f"{result}")
                else:
                    print("Status: No slots available yet.")
            
            elif response.status_code == 403:
                notify(f"⚠️ Noon Monitor 403 Forbidden. Check logs.")
                print("Error 403: Akamai/Bot protection triggered. Cookie may be invalid for this IP.")
            
            elif response.status_code == 401:
                notify("⚠️ Noon Session Expired! Please update the NOON_COOKIE in Render.")
                print("Error 401: Unauthorized.")
            
            else:
                notify(f"⚠️ Something wrong happened. {response.status_code}")
                print(f"Unexpected Status: {response.status_code}")

        except Exception as e:
            print(f"Loop Error: {e}")

        # Wait 5 minutes (300 seconds) before checking again
        time.sleep(300)

# --- WEB SERVER ROUTES ---
@app.route('/')
def health_check():
    return f"Noon Monitor is Active. Last check attempted at {datetime.now().strftime('%H:%M:%S')}"

if __name__ == "__main__":
    # 1. Start the monitoring loop in a separate thread so the web server can run
    monitor_thread = threading.Thread(target=check_noon_slots, daemon=True)
    monitor_thread.start()

    # 2. Start the Flask server (Render binds to the PORT variable)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)