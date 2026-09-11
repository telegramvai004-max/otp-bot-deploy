import random
import time

import otp_bot

TOTAL = 1000
# other countries (exclude nothing special; use the full table)
COUNTRIES = ["84", "1", "44", "91", "86", "81", "82", "62", "90", "7",
             "55", "33", "49", "39", "34", "31", "46", "48", "380", "971",
             "966", "92", "880", "63", "66", "60", "65", "27", "234", "20",
             "213", "98", "51", "52", "57", "233"]


def send_one():
    cc = random.choice(COUNTRIES)
    local = "".join(str(random.randint(0, 9)) for _ in range(9))
    number = cc + local
    otp = str(random.randint(100000, 999999))  # Facebook always 6-digit
    msg = f"Facebook code is {otp}"
    rec = {"num": number, "cli": "facebook", "message": msg,
           "dt": time.strftime("%Y-%m-%d %H:%M:%S")}
    text = otp_bot.format_record(rec)
    ok = otp_bot.tg_send(text, otp)
    print(f"[{'OK' if ok else 'FAIL'}] FB {cc} OTP={otp} num=+{number}")
    return ok


def main():
    print(f"Sending {TOTAL} Facebook 6-digit OTPs (random countries, 2/s)...")
    sent = 0
    while sent < TOTAL:
        try:
            for _ in range(2):  # 2 OTPs per second
                if sent >= TOTAL:
                    break
                if send_one():
                    sent += 1
                else:
                    time.sleep(5)
            time.sleep(1)
        except KeyboardInterrupt:
            print(f"\nStopped after {sent}/{TOTAL}.")
            break
    print(f"Done. Sent {sent} OTPs.")


if __name__ == "__main__":
    main()