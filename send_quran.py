#!/usr/bin/env python3
# send_quran.py  — GitHub Actions ready

import os
import sys
import telebot
import jdatetime
import datetime

# ---------- خواندن تنظیمات از environment (GitHub Secrets) ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # e.g. @icspi11 or numeric id

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN environment variable is not set.", file=sys.stderr)
    sys.exit(1)
if not CHAT_ID:
    print("ERROR: CHAT_ID environment variable is not set.", file=sys.stderr)
    sys.exit(1)

# ---------- مسیر تصاویر داخل ریپو (Linux) ----------
QURAN_PATH = "quran_pages"   # پوشه‌ای که در ریپو قرار می‌دهی

# ---------- آماده‌سازی ربات ----------
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# ---------- ترجمه روز هفته به فارسی ----------
def get_fa_weekday(gdate):
    days = {
        "Saturday": "شنبه",
        "Sunday": "یک‌شنبه",
        "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه",
        "Wednesday": "چهارشنبه",
        "Thursday": "پنج‌شنبه",
        "Friday": "جمعه",
    }
    return days.get(gdate.strftime("%A"), gdate.strftime("%A"))

# ---------- ترجمه ماه میلادی به فارسی (اختیاری) ----------
MONTHS_GR_FA = {
    "January":"ژانویه","February":"فوریه","March":"مارس","April":"آوریل",
    "May":"می","June":"ژوئن","July":"ژوئیه","August":"اوت",
    "September":"سپتامبر","October":"اکتبر","November":"نوامبر","December":"دسامبر"
}

# ---------- ذکرهای روزانه (قابل ویرایش) ----------
daily_zikr = [
    "«یا رَبَّ الْعالَمین»",
    "«سُبْحَانَ اللّهِ»",
    "«الْحَمْدُ لِلّهِ»",
    "«اللّهُ أَكْبَرُ»",
    "«لا إله إلا الله»",
    "«أستغفر الله»",
    "«اللهم صل علی محمد و آل محمد»"
]

# ---------- بررسی پوشه تصاویر ----------
if not os.path.isdir(QURAN_PATH):
    print(f"ERROR: images folder not found: {QURAN_PATH}", file=sys.stderr)
    sys.exit(1)

pages = sorted([f for f in os.listdir(QURAN_PATH) if f.lower().endswith(('.png','.jpg','.jpeg'))])
if not pages:
    print(f"ERROR: no image files found in {QURAN_PATH}", file=sys.stderr)
    sys.exit(1)

# ---------- تعیین index صفحه بر اساس روز شمسی (ثابت و تکرارشونده) ----------
today_j = jdatetime.date.today()
# استفاده از day of year شمسی برای متنوع بودن در طول سال
day_of_year = today_j.timetuple().tm_yday
idx = (day_of_year - 1) % len(pages)
page_file = pages[idx]
page_path = os.path.join(QURAN_PATH, page_file)
page_number = idx + 1

# ---------- ساخت تاریخ‌ها و متن فارسی ----------
today_g = datetime.date.today()
sh_weekday = get_fa_weekday(today_g)
sh_date = today_j.strftime("%d %B %Y")  # به صورت 02 آذر 1404
gr_month_fa = MONTHS_GR_FA.get(today_g.strftime("%B"), today_g.strftime("%B"))
gr_date_fa = f"{today_g.day} {gr_month_fa} {today_g.year}"

# تلاش برای تبدیل به هجری (در صورت وجود hijridate)
try:
    from hijridate import Gregorian
    hijri = Gregorian(today_g.year, today_g.month, today_g.day).to_hijri()
    hijri_date = f"{hijri.day} {hijri.month_name()} {hijri.year}"
except Exception:
    hijri_date = ""

# انتخاب ذکر بر اساس روز شمسی (مثال: براساس شماره روز)
zikr = daily_zikr[today_j.day % len(daily_zikr)]

recommendation = (
    "هر روز حتماً قرآن بخوانید حتّی روزی نیم صفحه، روزی یک صفحه بخوانید، "
    "امّا ترک نشود."
)

caption = (
    f"⭕️ هر روز یک صفحه قرآن بخوانیم\n\n"
    f"🔹 امروز؛ صفحه {page_number}\n\n"
    f"✏️ توصیه:\n{recommendation}\n\n"
    f"📆 امروز {sh_weekday}\n"
    f"☀️ {sh_date} هجری شمسی\n"
    f"🌙 {hijri_date} هجری قمری\n"
    f"🎄 {gr_date_fa} میلادی\n\n"
    f"📿 #ذکر امروز ۱۰۰ مرتبه:\n{zikr}"
)

# ---------- ارسال عکس ----------
print("DEBUG: sending", page_path)
try:
    with open(page_path, "rb") as photo:
        bot.send_photo(CHAT_ID, photo, caption=caption)
    print("OK: sent", page_file)
except Exception as e:
    print("ERROR: failed to send photo:", e, file=sys.stderr)
    sys.exit(1)
