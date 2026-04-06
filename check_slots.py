import os
import requests
import sys

# Secrets from GitHub environment
TELEGRAM_TOKEN = os.getenv('TG_TOKEN')
CHAT_ID = os.getenv('TG_CHAT_ID')
NOON_COOKIE = os.getenv('NOON_COOKIE')

def notify(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

def check_noon():
    url = 'https://fbn.noon.partners/_svc/inbound-scheduler/day/fbn/v1/capacity'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'cookie': NOON_COOKIE,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-locale': 'en-eg',
        'x-project': 'PRJ452348'
    }

    # Your payload from cURL
    data = {
        "asn_nr": "A05094139PN",
        "id_partner": 452348,
        "total_units": 949,
        "warehouse_to": "CAI04",
        "id_value": "3456"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            # Logic: If the 'days' array has any items, a slot exists
            # Adjust the key 'days' based on the actual response structure
            if result.get('days') and len(result['days']) > 0:
                notify("🚀 NOON SLOT FOUND! Go schedule now: https://fbn.noon.partners/")
            else:
                print("No slots available currently.")
        else:
            print(f"Failed to check: {response.status_code}")
            notify(f"⚠️ Noon Check Failed\nStatus: {response.status_code}\nResponse: {response.text[:100]}")
            if response.status_code == 401:
                notify("⚠️ Noon Cookie Expired! Please update your GitHub Secret.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_noon()