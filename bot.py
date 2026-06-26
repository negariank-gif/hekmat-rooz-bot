import os
import requests
import random
import json
from PIL import Image, ImageDraw, ImageFont
import io

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

gradients = [
    [(25, 25, 112), (72, 61, 139)],
    [(44, 62, 80), (52, 152, 219)],
    [(39, 60, 54), (56, 132, 95)],
    [(74, 20, 60), (130, 50, 100)],
    [(80, 50, 20), (180, 120, 40)],
    [(20, 50, 80), (40, 100, 140)],
    [(60, 20, 20), (140, 60, 40)],
    [(30, 30, 60), (80, 40, 120)],
]

def get_content_from_gemini():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = """یک پست کوتاه و زیبا برای کانال تلگرام حکمت و عرفان بنویس.
    
محتوا میتواند یکی از این موارد باشد:
- نقل قول از بزرگان مثل مولانا، حافظ، سعدی، فردوسی، الهی قمشه‌ای، تولستوی، دوستایوفسکی
- یک جمله احساسی و دردناک درباره تنهایی، عشق، یا زندگی
- یک حکمت کوتاه درباره رشد و بیداری
- یک جمله انگیزشی عمیق

فرمت پاسخ را دقیقاً اینگونه بنویس (فقط JSON، بدون توضیح اضافه):
{"text": "متن جمله یا نقل قول", "author": "نام گوینده یا منبع", "tags": "#هشتگ۱ #هشتگ۲ #هشتگ۳"}

نکات:
- متن فارسی باشد
- از نقل قول‌های واقعی و معروف استفاده کن
- هشتگ‌ها مرتبط با موضوع باشند
- اگر جمله احساسی است بنویس: "author": "دل نوشت"
"""

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9}
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        text = text.strip().replace('```json', '').replace('```', '').strip()
        quote = json.loads(text)
        return quote
    else:
        print(f"خطای Gemini: {response.text}")
        return None

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

    draw.rectangle([(80, 80), (width-80, 84)], fill=(255, 215, 0))
    draw.rectangle([(80, height-84), (width-80, height-80)], fill=(255, 215, 0))

    try:
        font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 46)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font_quote = ImageFont.load_default()
        font_author = font_quote

    draw.text((width//2, 180), "❝", font=font_quote, fill=(255, 215, 0), anchor="mm")

    max_chars = 24
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

    total_text_height = len(lines) * 68
    start_y = (height - total_text_height) // 2 - 40

    for i, line in enumerate(lines):
        y = start_y + i * 68
        draw.text((width//2, y), line, font=font_quote, fill=(255, 255, 255), anchor="mm")

    draw.rectangle([(width//2 - 80, start_y + total_text_height + 25),
                    (width//2 + 80, start_y + total_text_height + 28)],
                   fill=(255, 215, 0))

    draw.text((width//2, start_y + total_text_height + 65),
              f"— {author}", font=font_author, fill=(255, 215, 0), anchor="mm")

    draw.text((width//2, height - 115), "@sanchobook",
              font=font_author, fill=(200, 200, 200), anchor="mm")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def send_quote():
    quote = get_content_from_gemini()
    
    if not quote:
        print("خطا در دریافت از Gemini")
        return

    print(f"محتوا دریافت شد: {quote['author']}")
    
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
        print(f"تصویر ارسال شد!")
    else:
        print(f"خطای تلگرام: {response.text}")

if __name__ == "__main__":
    send_quote()
