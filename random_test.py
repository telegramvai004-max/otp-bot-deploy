import argparse
import random
import sys
import time

import otp_bot
import config

# country code -> name
COUNTRIES = {
    "84": "Vietnam", "1": "USA", "44": "UK", "91": "India",
    "86": "China", "81": "Japan", "82": "Korea", "62": "Indonesia",
    "90": "Turkey", "7": "Russia", "55": "Brazil", "33": "France",
    "49": "Germany", "39": "Italy", "34": "Spain", "31": "Netherlands",
    "46": "Sweden", "48": "Poland", "971": "UAE", "966": "Saudi",
    "92": "Pakistan", "880": "Bangladesh", "63": "Philippines",
    "66": "Thailand", "60": "Malaysia", "65": "Singapore", "27": "South Africa",
    "234": "Nigeria", "20": "Egypt", "98": "Iran", "46": "Sweden",
    "233": "Ghana", "51": "Peru", "52": "Mexico", "57": "Colombia",
}

APPS = [
    "facebook", "whatsapp", "telegram", "instagram", "google", "gmail",
    "outlook", "microsoft", "paypal", "amazon", "netflix", "uber", "linkedin",
    "discord", "twitter", "tiktok", "snapchat", "apple", "binance", "coinbase",
    "viber", "skype", "steam", "epic", "blizzard", "hitv", "ebay", "zalando",
    "swiggy", "zomato", "deliveroo", "airtel", "jio", "vi",
]

APP_MSGS = {
    "facebook": "Facebook code is {otp}",
    "whatsapp": "WhatsApp verification code {otp}",
    "telegram": "Your Telegram code is {otp}",
    "instagram": "Instagram code: {otp}",
    "google": "Your Google verification code is {otp}",
    "paypal": "PayPal security code {otp}",
    "amazon": "Amazon OTP: {otp}",
    "netflix": "Netflix login code {otp}",
    "binance": "Binance verification code {otp}",
    "coinbase": "Coinbase code {otp}",
}


def random_number(cc):
    local_len = random.randint(8, 10)
    local = "".join(str(random.randint(0, 9)) for _ in range(local_len))
    return cc + local


def random_otp(length=6):
    # Telegram OTPs are exactly 5 digits (Telegram only accepts 5-digit codes)
    lo = 10 ** (length - 1)
    hi = 10 ** length - 1
    return str(random.randint(lo, hi))


def send_one(country=None, app=None):
    if country and country in COUNTRIES:
        cc = country
        country_name = COUNTRIES[cc]
    else:
        cc = random.choice(list(COUNTRIES.keys()))
        country_name = COUNTRIES[cc]
    if not app:
        app = random.choice(APPS)
    number = random_number(cc)
    # Telegram -> exactly 5 digits; everything else -> 6 digits
    otp_len = 5 if app == "telegram" else 6
    otp = random_otp(otp_len)
    msg = (APP_MSGS.get(app) or f"{app} verification code is {otp}").format(otp=otp)
    rec = {"num": number, "cli": app, "message": msg, "dt": time.strftime("%Y-%m-%d %H:%M:%S")}
    text = otp_bot.format_record(rec)
    ok = otp_bot.tg_send(text, otp)
    print(f"[{'OK' if ok else 'FAIL'}] {country_name} {app} {otp} {number}")
    return ok


def main():
    p = argparse.ArgumentParser(description="Send random/fixed fake OTPs to the group")
    p.add_argument("--country", "-c", default=None, help="Country code, e.g. 39 for Italy (default: random)")
    p.add_argument("--app", "-a", default=None, help="App name, e.g. telegram (default: random)")
    p.add_argument("--count", "-n", type=int, default=0, help="How many to send (default: unlimited)")
    p.add_argument("--delay", "-d", type=float, default=1.5, help="Delay between sends in seconds")
    args = p.parse_args()

    if args.count and args.count <= 0:
        print("Count must be > 0")
        sys.exit(1)

    desc = []
    if args.country:
        desc.append(f"country {args.country}({COUNTRIES.get(args.country, '?')})")
    else:
        desc.append("random country")
    desc.append(f"app {args.app or 'random'}")
    target = f"{args.count} OTPs" if args.count else "unlimited OTPs"
    print(f"Sending {target} | {' '.join(desc)} (CTRL+C to stop)...")

    sent = 0
    while True:
        try:
            if not send_one(country=args.country, app=args.app):
                time.sleep(5)
            sent += 1
            if args.count and sent >= args.count:
                print(f"Done. Sent {sent} OTPs.")
                break
            time.sleep(max(0.2, args.delay))
        except KeyboardInterrupt:
            print(f"\nStopped after {sent} OTPs.")
            break


if __name__ == "__main__":
    main()
