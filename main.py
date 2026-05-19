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
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,aed&include_24hr_change=true"
        response = requests.get(url, timeout=15)
        data = response.json()
        coins = []
        for coin in COINS:
            if coin in data:
                coins.append({
                    "name": coin,
                    "price_usd": data[coin].get("usd", "N/A"),
                    "price_aed": data[coin].get("aed", "N/A"),
                    "change_24h": data[coin].get("usd_24h_change", 0),
                })
        return coins
    except Exception as e:
        print(f"Crypto error: {e}")
        return []

def check_urgent(coins):
    urgent = []
    for coin in coins:
        change = abs(float(coin.get("change_24h", 0)))
        if change >= 15:
            direction = "surged" if coin["change_24h"] > 0 else "crashed"
            urgent.append(f"{coin['name'].upper()} {direction} {coin['change_24h']:.1f}% — now ${coin['price_usd']}")
    return urgent

def generate_report(coins):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""You are Louka's personal crypto advisor. 13, Dubai, MAX 1,500 AED crypto. Parents help buy.

Today: {datetime.now().strftime("%B %d, %Y")}
Data: {json.dumps(coins, indent=2)}

Hey Louka 👋 Crypto check for today:

🚀 TOP PICK TODAY
- [Coin] at [AED] — [why]
- Suggested: [X] AED

💰 YOUR MOVES TODAY
- [X] AED → [Coin] — [reason]
- [X] AED → [Coin] — [reason]
- Keep rest as cash

🚫 AVOID TODAY
- [Coin] — [reason]

⚠️ MARKET MOOD
- [One sentence]

👀 WATCH THIS WEEK
- [One thing]

Max 200-400 AED today."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def hourly_check():
    print(f"Hourly crypto check - {datetime.now()}")
    coins = get_crypto_data()
    urgent = check_urgent(coins)
    if urgent:
        reason = urgent[0]
        alert = f"🚨🔴🚨🔴🚨🔴🚨🔴🚨\n\n<b>LOUKA — ACT NOW</b>\n\n{reason}\n\n→ Check Binance immediately\n\n⏰ {datetime.now().strftime('%H:%M')} Dubai time"
        send_telegram(alert)
        print("URGENT CRYPTO ALERT SENT")

def daily_job():
    print(f"Running crypto scan - {datetime.now()}")
    coins = get_crypto_data()
    report = generate_report(coins)
    message = f"₿ <b>Your Daily Crypto Brief - {datetime.now().strftime('%B %d, %Y')}</b>\n\n{report}"
    send_telegram(message)

print("Crypto Agent running!")
print(f"Started: {datetime.now()}")
daily_job()

schedule.every().day.at("06:00").do(daily_job)
schedule.every(1).hours.do(hourly_check)

while True:
    schedule.run_pending()
    time.sleep(60)
