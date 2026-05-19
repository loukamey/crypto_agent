import requests
import schedule
import time
from datetime import datetime
import json
import os
import anthropic

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_TOKEN = "8618649387:AAEjueDVhm8fZDOf4NAFIE9j2XXZmooqQ7U"
TELEGRAM_CHAT_ID = "8526660731"

COINS = ["bitcoin", "ethereum", "solana", "binancecoin", "ripple", "cardano", "avalanche-2", "chainlink"]

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("Telegram message sent!")
        else:
            print(f"Telegram error: {response.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

def get_crypto_data():
    try:
        ids = ",".join(COINS)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,aed&include_24hr_change=true&include_24hr_vol=true"
        response = requests.get(url, timeout=15)
        data = response.json()
        coins = []
        for coin in COINS:
            if coin in data:
                coins.append({
                    "name": coin,
                    "price_usd": data[coin].get("usd", "N/A"),
                    "price_aed": data[coin].get("aed", "N/A"),
                    "change_24h": data[coin].get("usd_24h_change", "N/A"),
                    "volume": data[coin].get("usd_24h_vol", "N/A"),
                })
        return coins
    except Exception as e:
        print(f"Crypto error: {e}")
        return []

def generate_report(coins):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""You are Louka's personal crypto advisor. Louka is 13, lives in Dubai, has 9,000 AED total. He should put MAX 1,500 AED into crypto — small amounts only. Parents are involved in actual buying.

Today: {datetime.now().strftime("%B %d, %Y")}
Crypto data: {json.dumps(coins, indent=2)}

Write his daily crypto brief in this EXACT bullet point format — personal, direct, like texting a friend:

Hey Louka 👋 Crypto check for today:

🚀 TOP PICK TODAY
- [Coin] at [AED price] — [2-3 sentences why, be specific about the 24h movement]
- Suggested amount: [X] AED

💰 YOUR MOVES TODAY
- [X] AED → [Coin] — [one line reason]
- [X] AED → [Coin] — [one line reason]
- Keep the rest as cash

🚫 AVOID TODAY
- [Coin] — [one line reason why not today]

⚠️ MARKET MOOD
- [One sentence on overall crypto market today]

👀 WATCH THIS WEEK
- [One thing to watch for this week in crypto]

Total suggested today: MAX 200-400 AED. Crypto is volatile — small amounts only. Keep it tight."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def daily_job():
    print(f"Running crypto scan - {datetime.now()}")
    coins = get_crypto_data()
    print(f"Got {len(coins)} coins")
    report = generate_report(coins)
    message = f"₿ <b>Your Daily Crypto Brief - {datetime.now().strftime('%B %d, %Y')}</b>\n\n{report}"
    send_telegram(message)

print("Crypto Intelligence Agent is running!")
print(f"Started at: {datetime.now()}")
print("Sending crypto report now...")
daily_job()

schedule.every().day.at("06:00").do(daily_job)

while True:
    schedule.run_pending()
    time.sleep(60)
