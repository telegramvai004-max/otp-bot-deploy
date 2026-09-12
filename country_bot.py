import random
import threading
import time

import requests

import config
import otp_bot

API = f"https://api.telegram.org/bot{config.BOT_TOKEN}/{{method}}"
RATE = 2  # OTPs per second

PLATFORMS = [
    {"key": "whatsapp", "label": "💬 WhatsApp", "app": "whatsapp", "digits": 6},
    {"key": "facebook", "label": "📘 Facebook", "app": "facebook", "digits": 6},
    {"key": "telegram", "label": "✈️ Telegram", "app": "telegram", "digits": 5},
]
PLAT_BY_KEY = {p["key"]: p for p in PLATFORMS}


def tg(method, **kw):
    try:
        r = requests.post(API.format(method=method), json=kw, timeout=60)
        return r.json()
    except Exception as e:
        print("tg error:", e)
        return None


# ---- build the country list from otp_bot tables ----
def build_countries():
    seen = {}
    for prefix, flag in otp_bot.PREFIX_FLAGS:
        if prefix in seen:
            continue
        seen[prefix] = (flag, otp_bot.COUNTRY_SHORT.get(prefix, prefix),
                        otp_bot.COUNTRY_NAMES.get(prefix, prefix))
    items = [(prefix, flag, short, name) for prefix, (flag, short, name) in seen.items()]
    items.sort(key=lambda x: x[3])
    return items


COUNTRIES = build_countries()
PER_PAGE = 8


def platform_menu():
    rows = []
    for p in PLATFORMS:
        rows.append([{"text": p["label"], "callback_data": f"pl:{p['key']}"}])
    rows.append([{"text": "🛑 Stop Sending", "callback_data": "stop"}])
    return {"inline_keyboard": rows}


def country_menu(plat_key, page=0):
    total = len(COUNTRIES)
    pages = (total + PER_PAGE - 1) // PER_PAGE
    page = max(0, min(page, pages - 1))
    start = page * PER_PAGE
    rows = []
    for p, flag, short, name in COUNTRIES[start:start + PER_PAGE]:
        rows.append([{"text": f"{flag} {name} ({short})",
                      "callback_data": f"sel:{plat_key}:{p}"}])
    nav = []
    if page > 0:
        nav.append({"text": "⬅️", "callback_data": f"pg:{plat_key}:{page - 1}"})
    nav.append({"text": f"{page + 1}/{pages}", "callback_data": "noop"})
    if page < pages - 1:
        nav.append({"text": "➡️", "callback_data": f"pg:{plat_key}:{page + 1}"})
    rows.append(nav)
    rows.append([{"text": "⬅️ Back to platforms", "callback_data": "back"}])
    rows.append([{"text": "🛑 Stop Sending", "callback_data": "stop"}])
    return {"inline_keyboard": rows}


CURRENT = {"app": None, "flag": None, "cc": None, "name": None}
_thread = None
_send_stop = threading.Event()


def stop_sender():
    global _thread, _send_stop
    _send_stop.set()
    if _thread and _thread.is_alive():
        _thread.join(timeout=3)
    _thread = None
    CURRENT.update(app=None, flag=None, cc=None, name=None)


def start_sender(plat_key, cc, flag, name, chat_id):
    global _thread, _send_stop
    stop_sender()
    _send_stop = threading.Event()
    plat = PLAT_BY_KEY[plat_key]

    def worker():
        while not _send_stop.is_set():
            local = "".join(str(random.randint(0, 9)) for _ in range(9))
            number = cc + local
            otp_len = plat["digits"]
            otp = str(random.randint(10 ** (otp_len - 1), 10 ** otp_len - 1))
            msg = f"Your {plat['app']} code is {otp}"
            rec = {"num": number, "cli": plat["app"], "message": msg}
            text = otp_bot.format_record(rec)
            ok = otp_bot.tg_send(text, otp)  # sends to the OTP group
            print(f"[{'OK' if ok else 'FAIL'}] {name} {plat['app']} OTP={otp} num=+{number}")
            if not ok:
                time.sleep(5)
            for _ in range(RATE):
                if _send_stop.is_set():
                    break
                time.sleep(1.0 / RATE)

    CURRENT.update(app=plat["key"], flag=flag, cc=cc, name=name)
    _thread = threading.Thread(target=worker, daemon=True)
    _thread.start()
    tg_send(chat_id,
            f"🚀 Started {plat['label']} test OTPs for <b>{flag} {name}</b> (+{cc}), "
            f"{otp_len} digits · {RATE} OTP/s.\n"
            f"Use /stop to halt.")


def tg_send(chat_id, text, markup=None):
    kw = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if markup:
        kw["reply_markup"] = markup
    return tg("sendMessage", **kw)


def tg_edit(chat_id, message_id, text, markup=None):
    kw = {"chat_id": chat_id, "message_id": message_id, "text": text,
          "parse_mode": "HTML"}
    if markup:
        kw["reply_markup"] = markup
    return tg("editMessageText", **kw)


def handle_command(chat_id, text):
    text = (text or "").strip()
    if text.startswith("/start"):
        tg_send(chat_id, "🌍 <b>Select a platform:</b>\n"
                         "Then choose a country — OTPs will be sent to the OTP group "
                         "for numbers in that country.",
                platform_menu())
        return True
    if text.startswith("/stop"):
        stop_sender()
        tg_send(chat_id, "🛑 Stopped sending OTPs.")
        return True
    if text.startswith("/status"):
        if CURRENT["cc"]:
            plat = PLAT_BY_KEY[CURRENT["app"]]["label"]
            tg_send(chat_id, f"Currently sending: {plat} · {CURRENT['flag']} "
                             f"{CURRENT['name']} (+{CURRENT['cc']}) · {RATE} OTP/s")
        else:
            tg_send(chat_id, "Not sending any OTPs right now.")
        return True
    if text.startswith("/ping"):
        tg_send(chat_id, "🟢 Bot is online and responding.")
        return True
    if text.startswith("/help"):
        tg_send(chat_id,
                "🛠 <b>Available commands</b>\n\n"
                "/start — open the platform & country menu\n"
                "/ping — check the bot is alive\n"
                "/status — see what is currently being sent\n"
                "/stop — stop all OTP sending\n"
                "/help — this list\n\n"
                "⚙️ <b>AI issues?</b> The bot automatically restarts and "
                "sends an alert here if it crashes.")
        return True
    return False


def handle_callback(cb):
    chat_id = (cb.get("message") or {}).get("chat", {}).get("id")
    msg_id = (cb.get("message") or {}).get("message_id")
    data = cb.get("data", "")
    tg("answerCallbackQuery", callback_query_id=cb["id"])
    if not chat_id or not msg_id:
        return
    if data == "stop":
        stop_sender()
        tg_edit(chat_id, msg_id, "🛑 <b>Stopped sending OTPs.</b>", platform_menu())
    elif data == "back":
        tg_edit(chat_id, msg_id, "🌍 <b>Select a platform:</b>", platform_menu())
    elif data == "noop":
        pass
    elif data.startswith("pl:"):
        plat_key = data.split(":", 1)[1]
        plat = PLAT_BY_KEY[plat_key]["label"]
        tg_edit(chat_id, msg_id,
                f"🌍 <b>Select a country for {plat}:</b>", country_menu(plat_key, 0))
    elif data.startswith("pg:"):
        _, plat_key, page = data.split(":")
        plat = PLAT_BY_KEY[plat_key]["label"]
        tg_edit(chat_id, msg_id,
                f"🌍 <b>Select a country for {plat}:</b>",
                country_menu(plat_key, int(page)))
    elif data.startswith("sel:"):
        _, plat_key, cc = data.split(":")
        for p, flag, short, name in COUNTRIES:
            if p == cc:
                start_sender(plat_key, cc, flag, name, chat_id)
                break


def main():
    print("Country-menu OTP sender bot running...")
    offset = 0
    while True:
        try:
            upd = tg("getUpdates", offset=offset, timeout=30,
                     allowed_updates=["message", "callback_query"])
            if not upd or not upd.get("ok"):
                time.sleep(1)
                continue
            for u in upd["result"]:
                offset = u["update_id"] + 1
                if "callback_query" in u:
                    handle_callback(u["callback_query"])
                elif u.get("message", {}).get("text") is not None:
                    chat_id = u["message"]["chat"]["id"]
                    txt = u["message"]["text"]
                    if txt.startswith("/"):
                        handle_command(chat_id, txt)
        except KeyboardInterrupt:
            print("\nStopped.")
            stop_sender()
            break
        except Exception as e:
            print("loop error:", e)
            try:
                tg_send(config.CHAT_ID,
                        f"⚠️ <b>Bot loop error</b>\n<code>{e}</code>\n"
                        f"Restarting in 5s…")
            except Exception:
                pass
            time.sleep(5)


if __name__ == "__main__":
    main()