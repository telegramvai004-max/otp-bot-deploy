# HOW TO PUT YOUR BOT ONLINE (24/7) — SIMPLE GUIDE

Do these steps in order, on a phone or computer. Nothing here writes code —
everything is button-clicking.

------------------------------------------------------------------------
STEP 1 — CREATE A GITHUB ACCOUNT
------------------------------------------------------------------------
1. Open https://github.com/signup in a browser
2. Enter your email, create a password, pick a username
3. Click "Create account", verify the puzzle/email
4. You're done — keep this tab open

------------------------------------------------------------------------
STEP 2 — UPLOAD YOUR BOT FILES TO GITHUB
------------------------------------------------------------------------
1. Go to https://github.com/new
2. Repo name: type  otpbot   (anything is fine)
3. Choose Public or Private (either works)
4. Click "Create repository"
5. On the new page click the text "uploading an existing file"
6. Click "choose your files" and select these files from your Desktop
   folder "hadi bot":
   - config.py
   - otp_bot.py
   - country_bot.py
   - run_server.py
   - requirements.txt
   - Dockerfile
7. Scroll down, click "Commit changes"

Your files are now online. 

------------------------------------------------------------------------
STEP 3 — CREATE A FREE RENDER ACCOUNT
------------------------------------------------------------------------
1. Open https://render.com
2. Click "Get Started" / "Sign Up Free"
3. Choose "Sign up with GitHub" (easiest) — it logs you in with your
   GitHub account, no new password needed
4. Follow the confirmation emails if any

------------------------------------------------------------------------
STEP 4 — CREATE YOUR FREE WEB SERVICE
------------------------------------------------------------------------
1. On the Render dashboard click blue button "+ New"
2. Click "Web Service"
3. Pick your "otpbot" repository, click "Connect"
4. Settings screen:
   - Name:        otp-bot
   - Region:      Singapore (or whatever is listed)
   - Language:    leave as detected
   - Build Command:  leave empty  (Docker does it)
   - Start Command:   leave empty  (Docker does it)
   - Instance Type:   choose FREE
5. Click "Create Web Service"
6. Wait ~3 minutes. You'll see "Deploy succeeded / Live"
7. Your bot gets an address like  https://otp-bot.onrender.com

------------------------------------------------------------------------
STEP 5 — KEEP IT AWAKE FOREVER (free)
------------------------------------------------------------------------
Render free services sleep after 15 minutes. Fix it with UptimeRobot:
1. Open https://uptimerobot.com  → "Create free account"
2. Log in → click "+ Add New Monitor"
3. Monitor Type:   HTTP(s)
4. Friendly Name:  otp-bot
5. URL:            https://otp-bot.onrender.com   (your Render address)
6. Monitoring Interval:  "Every 5 minutes"
7. Click "Create Monitor"

Now something pings your bot every 5 minutes so it never sleeps.

------------------------------------------------------------------------
FINISHED — TEST IT
------------------------------------------------------------------------
Open Telegram, message @yaufee1bot  →  send /start
You should see the platform buttons (WhatsApp / Facebook / Telegram).
Click one, pick a country, and OTPs start being sent.

Your PC can now be turned OFF — the bot lives on Render's servers 24/7.

------------------------------------------------------------------------
TROUBLESHOOTING
------------------------------------------------------------------------
- "/start does nothing": the deploy is still building, wait 2-3 min
- Page shows error: click "Manual Deploy" → "Deploy latest commit" in Render
- Changed files locally? Re-upload them to GitHub — Render updates itself