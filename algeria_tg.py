import random
import time

import otp_bot

TOTAL = 1000
ALREADY_SENT = 382  # resume from where it stopped
CC = "213"  # Algeria


def send_one():
    local = "".join(str(random.randint(0, 9)) for _ in range(9))
    number = CC + local
    otp = str(random.randint(10000, 99999))  # Telegram is always 5 digits
    msg = f"Your Telegram code is {otp}"
    rec = {"num": number, "cli": "telegram", "message": msg,
           "dt": time.strftime("%Y-%m-%d %H:%M:%S")}
    text = otp_bot.format_record(rec)
    ok = otp_bot.tg_send(text, otp)
    print(f"[{'OK' if ok else 'FAIL'}] Algeria TG OTP={otp} num=+{number}")
    return ok


def main():
    print(f"Sending {TOTAL - ALREADY_SENT} more Algeria Telegram 5-digit OTPs (2/s, already {ALREADY_SENT})...")
    sent = 0
    while ALREADY_SENT + sent < TOTAL:
        try:
            for _ in range(2):  # 2 OTPs per second
                if ALREADY_SENT + sent >= TOTAL:
                    break
                if send_one():
                    sent += 1
                else:
                    time.sleep(5)
            time.sleep(1)
        except KeyboardInterrupt:
            print(f"\nStopped after {sent}/{TOTAL - ALREADY_SENT} more.")
            break
    print(f"Done. Sent {sent} more (total {ALREADY_SENT + sent}).")


if __name__ == "__main__":
    main()
