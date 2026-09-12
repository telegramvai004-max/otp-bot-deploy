"""Multi-provider AI assistant for the bot.

Supported providers (add keys via Render env vars - whichever you have):
  GEMINI_API_KEY   -> Google Gemini          (free @ aistudio.google.com)
  OPENAI_API_KEY   -> OpenAI GPT models
  GROQ_API_KEY     -> Groq (free fast models)
  DEEPSEEK_API_KEY -> DeepSeek (cheap strong models)

Conversation: each chat keeps a short rolling history so the AI can
remember the context. ask() tries providers in order and returns the
first successful reply.
"""
import os
import subprocess
import sys
import threading

import requests

MODELS = {
    "gemini": {
        "label": "🌀 Gemini",
        "env": "GEMINI_API_KEY",
        "model": "gemini-3.6-flash",
    },
    "openai": {
        "label": "🔵 OpenAI",
        "env": "OPENAI_API_KEY",
        "model": "gpt-4o-mini",
    },
    "groq": {
        "label": "⚡ Groq",
        "env": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
    },
    "deepseek": {
        "label": "🐋 DeepSeek",
        "env": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat",
    },
}

HISTORY = {}
HISTORY_LOCK = threading.Lock()
MAX_HISTORY = 10


def available():
    out = []
    for key, cfg in MODELS.items():
        if os.getenv(cfg["env"]):
            out.append((key, cfg))
    return out


def get_history(chat_id):
    with HISTORY_LOCK:
        return HISTORY.setdefault(int(chat_id), [])


def push_message(chat_id, role, content):
    with HISTORY_LOCK:
        h = HISTORY.setdefault(int(chat_id), [])
        h.append({"role": role, "content": content})
        if len(h) > MAX_HISTORY:
            del h[: len(h) - MAX_HISTORY]
    return h


def reset_history(chat_id):
    with HISTORY_LOCK:
        HISTORY[int(chat_id)] = []


def _call_gemini(cfg, messages):
    key = os.getenv(cfg["env"])
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{cfg['model']}:generateContent?key={key}")
    # convert chat messages into Gemini content parts
    contents = []
    for m in messages:
        contents.append({"role": "user" if m["role"] != "assistant" else "model",
                         "parts": [{"text": m["content"]}]})
    r = requests.post(url, json={"contents": contents}, timeout=90)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def _call_openai_compat(cfg, messages, base_url):
    key = os.getenv(cfg["env"])
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {key}"}
    r = requests.post(url, json={"model": cfg["model"], "messages": messages},
                      headers=headers, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def ask(chat_id, user_text):
    """Send user_text to the first available AI. Returns reply string."""
    push_message(chat_id, "user", user_text)
    messages = get_history(chat_id)
    last_err = None
    for key, cfg in available():
        try:
            if key == "gemini":
                reply = _call_gemini(cfg, messages)
            elif key == "openai":
                reply = _call_openai_compat(cfg, messages, "https://api.openai.com/v1")
            elif key == "groq":
                reply = _call_openai_compat(cfg, messages, "https://api.groq.com/openai/v1")
            elif key == "deepseek":
                reply = _call_openai_compat(cfg, messages, "https://api.deepseek.com/v1")
            else:
                continue
            push_message(chat_id, "assistant", reply)
            return reply, key
        except Exception as e:
            last_err = e
            print(f"[AI {key}] failed: {e}")
    return (f"⚠️ No AI is reachable right now. "
            f"Last error: {last_err}"), None


def ask_with(chat_id, user_text, key):
    """Force a specific provider. Raises/returns error string on failure."""
    push_message(chat_id, "user", user_text)
    messages = get_history(chat_id)
    cfg = MODELS[key]
    try:
        if key == "gemini":
            reply = _call_gemini(cfg, messages)
        elif key == "openai":
            reply = _call_openai_compat(cfg, messages, "https://api.openai.com/v1")
        elif key == "groq":
            reply = _call_openai_compat(cfg, messages, "https://api.groq.com/openai/v1")
        elif key == "deepseek":
            reply = _call_openai_compat(cfg, messages, "https://api.deepseek.com/v1")
        else:
            return f"❌ Unknown model '{key}'."
        push_message(chat_id, "assistant", reply)
        return reply
    except Exception as e:
        return (f"❌ {MODELS[key]['label']} failed:\n<code>{e}</code>\n"
                f"Try /model to switch.")


def run_python(code):
    """Execute python code snippet on the server. Returns output string."""
    try:
        p = subprocess.run([sys.executable, "-X", "utf8", "-c", code],
                           capture_output=True, text=True, timeout=30)
        out = p.stdout.strip()
        err = p.stderr.strip()
        if p.returncode != 0:
            return f"⚠️ Error (exit {p.returncode}):\n{err[:1500]}"
        return out if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "⏱️ Code took too long (>30s) and was stopped."
    except Exception as e:
        return f"⚠️ {e}"