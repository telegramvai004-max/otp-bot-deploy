from concurrent.futures import ThreadPoolExecutor
import time

import random_test

TARGET = 2000
BATCH = 10  # OTPs per 1-second tick

sent = 0
print(f"Sending {TARGET} Peru WhatsApp 6-digit OTPs...", flush=True)


def send_batch_one(_n):
    return 1 if random_test.send_one(country="51", app="whatsapp") else 0


while sent < TARGET:
    remaining = TARGET - sent
    count = min(BATCH, remaining)
    try:
        with ThreadPoolExecutor(max_workers=count) as ex:
            results = list(ex.map(send_batch_one, range(count)))
        sent += sum(results)
        time.sleep(1)
    except KeyboardInterrupt:
        break
print(f"Done. Sent {sent} OTPs.", flush=True)
