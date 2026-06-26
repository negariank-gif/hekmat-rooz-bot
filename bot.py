import os
import requests
import random
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

quotes = [
    {"text": "آنچه در آینه نتوان دید، در چشم دیگران توان یافت.", "author": "دکتر الهی قمشه‌ای", "tags": "#الهی_قمشه_ای #حکمت #عرفان"},
    {"text": "عشق یعنی دیدن خدا در چهره انسان‌ها.", "author": "دکتر الهی قمشه‌ای", "tags": "#الهی_قمشه_ای #عشق #عرفان"},
    {"text": "دل آدمی خانه خداست، آن را پاک نگه‌دار.", "author": "دکتر الهی قمشه‌ای", "tags": "#الهی_قمشه_ای #حکمت #دل"},
    {"text": "در خاموشی راز هستی نهفته است.", "author": "دکتر الهی قمشه‌ای", "tags": "#الهی_قمشه_ای #عرفان #سکوت"},
    {"text": "هر صبح که چشم می‌گشایی، هدیه‌ای تازه از خداست.", "author": "دکتر الهی قمشه‌ای", "tags": "#الهی_قمشه_ای #شکرگزاری #زندگی"},
    {"text": "بشر را محبت کافی است برای رستگاری.", "author": "لئو تولستوی", "tags": "#تولستوی #محبت #رستگاری"},
    {"text": "زندگی کوتاه است، پس آن را با کینه و نفرت تلف مکن.", "author": "لئو تولستوی", "tags": "#تولستوی #زندگی #حکمت"},
    {"text": "خوشبختی در راهی است که طی می‌کنی، نه در مقصدی که انتظارت را می‌کشد.", "author": "لئو تولستوی", "tags": "#تولستوی #خوشبختی #زندگی"},
    {"text": "توانا بود هر که دانا بود، ز دانش دل پیر برنا بود.", "author": "فردوسی", "tags": "#فردوسی #شاهنامه #حکمت"},
    {"text": "الهی چنان کن سرانجام کار، تو خشنود باشی و ما رستگار.", "author": "فردوسی", "tags": "#فردوسی #شاهنامه #دعا"},
    {"text": "بنی آدم اعضای یک پیکرند، که در آفرینش ز یک گوهرند.", "author": "سعدی", "tags": "#سعدی #گلستان #انسانیت"},
    {"text": "علم بی عمل چون درخت بی ثمر است.", "author": "سعدی", "tags": "#سعدی #علم #عمل"},
    {"text": "هر که را اسرار حق آموختند، مهر کردند و دهانش دوختند.", "author": "مولانا", "tags": "#مولانا #مثنوی #عرفان"},
    {"text": "از کوزه همان برون تراود که در اوست.", "author": "مولانا", "tags": "#مولانا #حکمت #اخلاق"},
    {"text": "سالک را سه نشانه است: کم خوردن، کم خفتن، کم گفتن.", "author": "خواجه عبدالله انصاری", "tags": "#انصاری #عرفان #سلوک"},
    {"text": "همه چیز را می توان از انسان گرفت، مگر آزادی انتخاب نگرش در هر شرایطی.", "author": "ویکتور فرانکل", "tags": "#فرانکل #آزادی #روانشناسی"},
]

gradients = [
    [(25, 25, 112), (72, 61, 139)],    # آبی تیره به بنفش
    [(44, 62, 80), (52, 152, 219)],     # سرمه‌ای به آبی
    [(39, 60, 54), (56, 132, 95)],      # سبز تیره به زمردی
    [(74, 20, 60), (130, 50, 100)],     # بنفش تیره به ارغوانی
    [(80, 50, 20), (180, 120, 40)],     # قهوه‌ای به طلایی
    [(20, 50, 80), (40, 100, 140)],     # آبی اقیانوسی
]

def create_gradient(width, height, color1, color2):
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return image

def create_image(quote_text, author):
    width, height = 1080, 1080
    colors = random.choice(gradients)
    img = create_gradient(width, height, colors[0], colors[1])
    draw = ImageDraw.Draw(img)

    # خط تزئینی بالا
    draw.rectangle([(80, 80), (width-80, 84)], fill=(255, 215, 0, 180))
    # خط تزئینی پایین
    draw.rectangle([(80, height-84), (width-80, height-80)], fill=(255, 215, 0, 180))

    try:
        font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        font_symbol = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
    except:
        font_quote = ImageFont.load_default()
        font_author = font_quote
        font_symbol = font_quote

    # علامت نقل قول
    draw.text((width//2, 180), "❝", font=font_symbol, fill=(255, 215, 0), anchor="mm")

    # متن جمله - شکستن به خطوط
    max_chars = 25
    words = quote_text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += (" " + word if current_line else word)
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # رسم متن وسط
    total_text_height = len(lines) * 65
    start_y = (height - total_text_height) // 2 - 30

    for i, line in enumerate(lines):
        y = start_y + i * 65
        draw.text((width//2, y), line, font=font_quote, fill=(255, 255, 255), anchor="mm")

    # خط جداکننده
    draw.rectangle([(width//2 - 80, start_y + total_text_height + 30),
                    (width//2 + 80, start_y + total_text_height + 33)],
                   fill=(255, 215, 0))

    # نام گوینده
    draw.text((width//2, start_y + total_text_height + 70),
              f"— {author}", font=font_author, fill=(255, 215, 0), anchor="mm")

    # نام کانال
    draw.text((width//2, height - 120), "@sanchobook",
              font=font_author, fill=(255, 255, 255, 150), anchor="mm")

    # ذخیره در حافظه
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def send_quote():
    quote = random.choice(quotes)
    img_bytes = create_image(quote['text'], quote['author'])

    caption = (
        f"<i>{quote['text']}</i>\n\n"
        f"— <b>{quote['author']}</b>\n\n"
        f"{quote['tags']} #حکمت #عرفان"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    response = requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "caption": caption,
        "parse_mode": "HTML"
    }, files={"photo": ("quote.png", img_bytes, "image/png")})

    if response.status_code == 200:
        print(f"تصویر ارسال شد: {quote['author']}")
    else:
        print(f"خطا: {response.text}")

if __name__ == "__main__":
    send_quote()
