import os
import requests
import random

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# گنجینه نقل‌قول‌ها
quotes = [
    {
        "text": "آنچه در آینه نتوان دید، در چشم دیگران توان یافت.",
        "author": "دکتر الهی قمشه‌ای"
    },
    {
        "text": "عشق یعنی دیدن خدا در چهره انسان‌ها.",
        "author": "دکتر الهی قمشه‌ای"
    },
    {
        "text": "بشر را محبت کافی است برای رستگاری.",
        "author": "لئو تولستوی"
    },
    {
        "text": "همه چیز را می‌توان از انسان گرفت، مگر آزادی انتخاب نگرش در هر شرایطی.",
        "author": "ویکتور فرانکل"
    },
    {
        "text": "توانا بود هر که دانا بود، ز دانش دل پیر برنا بود.",
        "author": "فردوسی"
    },
    {
        "text": "بنی‌آدم اعضای یک پیکرند، که در آفرینش ز یک گوهرند.",
        "author": "سعدی"
    },
    {
        "text": "از کوزه همان برون تراود که در اوست.",
        "author": "مولانا"
    },
    {
        "text": "آدمی را یک سخن ویران کند، یک سخن هم وحشی‌اش را رام کند.",
        "author": "مولانا"
    },
    {
        "text": "الهی! چنان کن سرانجام کار، تو خشنود باشی و ما رستگار.",
        "author": "فردوسی"
    },
    {
        "text": "خوشبختی در راهی است که طی می‌کنی، نه در مقصدی که انتظارت را می‌کشد.",
        "author": "لئو تولستوی"
    },
    {
        "text": "سالک را سه نشانه است: کم خوردن، کم خفتن، کم گفتن.",
        "author": "خواجه عبدالله انصاری"
    },
    {
        "text": "دل آدمی خانه خداست، آن را پاک نگه‌دار.",
        "author": "دکتر الهی قمشه‌ای"
    },
    {
        "text": "آنکه می‌داند و می‌داند که می‌داند، عاقل است؛ از او پیروی کن.",
        "author": "حکمت فارسی"
    },
    {
        "text": "زندگی کوتاه است، پس آن را با کینه و نفرت تلف مکن.",
        "author": "لئو تولستوی"
    },
    {
        "text": "هر که را اسرار حق آموختند، مهر کردند و دهانش دوختند.",
        "author": "مولانا"
    },
]

def send_quote():
    quote = random.choice(quotes)
    
    message = (
        f"🌿 *حکمت روز*\n\n"
        f"_{quote['text']}_\n\n"
        f"— *{quote['author']}*"
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print(f"✅ پیام ارسال شد: {quote['author']}")
    else:
        print(f"❌ خطا: {response.text}")

if __name__ == "__main__":
    send_quote()

