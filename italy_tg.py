import random
import time

import otp_bot

TOTAL = 1000


def send_italy_telegram():
    cc = "39"  # Italy
    local = "".join(str(random.randint(0, 9)) for _ in range(9))
    number = cc + local
    otp = str(random.randint(10000, 99999))  # 5-digit Telegram OTP
    msg = f"Your Telegram code is {otp}"
    rec = {
        "num": number,
        "cli": "telegram",
        "message": msg,
        "dt": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    text = otp_bot.format_record(rec)
    ok = otp_bot.tg_send(text, otp)  # button copies the 5-digit OTP
    print(f"[{'OK' if ok else 'FAIL'}] Italy TG OTP={otp} num=+{number}")
    return ok


def main():
    print(f"Sending {TOTAL} Telegram OTPs (Italy) to the group...")
    sent = 0
    while sent < TOTAL:
        try:
            if send_italy_telegram():
                sent += 1
            else:
                time.sleep(5)  # back off on failure
            time.sleep(2)
        except KeyboardInterrupt:
            print(f"\nStopped after {sent}/{TOTAL}.")
            break
    print(f"Done. Sent {sent} OTPs.")


if __name__ == "__main__":
    main()
