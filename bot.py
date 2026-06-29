import os
import requests
import random
import json
import datetime
from PIL import Image, ImageDraw, ImageFont
import io

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# دسته‌بندی جملات با رنگ و آیکون مخصوص
CATEGORIES = {
    "عرفان":     {"color1": (40, 20, 70),  "color2": (100, 50, 150), "icon": "🌙"},
    "عشق":       {"color1": (80, 20, 30),  "color2": (160, 50, 70),  "icon": "🌹"},
    "حکمت":      {"color1": (20, 50, 80),  "color2": (40, 100, 150), "icon": "✨"},
    "انگیزشی":   {"color1": (60, 40, 10),  "color2": (160, 110, 30), "icon": "⚡"},
    "دل_نوشت":   {"color1": (30, 50, 40),  "color2": (60, 120, 80),  "icon": "💚"},
    "فلسفه":     {"color1": (20, 20, 60),  "color2": (50, 50, 120),  "icon": "🔮"},
    "صبح":       {"color1": (80, 50, 10),  "color2": (200, 140, 40), "icon": "🌅"},
    "شب":        {"color1": (10, 10, 40),  "color2": (30, 30, 80),   "icon": "🌃"},
}

quotes_morning = [
    {"text": "هر صبح که چشم می‌گشایی، هدیه‌ای تازه از خداست. از این هدیه قدردانی کن.", "author": "دکتر الهی قمشه‌ای", "cat": "صبح", "tags": "#صبح #حکمت #عرفان", "en": "Every morning you open your eyes is a fresh gift from God."},
    {"text": "صبح را با شکرگزاری آغاز کن؛ روزی که با سپاس شروع شود، با برکت پایان می‌یابد.", "author": "دل نوشت", "cat": "صبح", "tags": "#صبح #حکمت #عرفان", "en": "Start the morning with gratitude; a day that begins with thanks ends with blessings."},
    {"text": "هر سپیده‌دم فرصتی است که دیروز نداشتی؛ غنیمت بشمارش.", "author": "دل نوشت", "cat": "صبح", "tags": "#صبح #حکمت #عرفان", "en": "Every dawn is an opportunity you didn't have yesterday; treasure it."},
    {"text": "صبح اول دوست خود باش، بعد به دنبال دوست دیگر برو.", "author": "دل نوشت", "cat": "صبح", "tags": "#صبح #حکمت #عرفان", "en": "In the morning, first be your own friend, then seek others."},
    {"text": "با طلوع آفتاب، امید تازه‌ای در دل بکار؛ که هر روز بذر جدیدی است.", "author": "دل نوشت", "cat": "صبح", "tags": "#صبح #حکمت #عرفان", "en": "With the sunrise, plant fresh hope in your heart; every day is a new seed."},
]

quotes_night = [
    {"text": "شب که می‌شود، دل می‌خواهد سکوت؛ که در سکوت، خدا سخن می‌گوید.", "author": "دل نوشت", "cat": "شب", "tags": "#شب #حکمت #عرفان", "en": "When night comes, the heart craves silence; for in silence, God speaks."},
    {"text": "پیش از خواب از خود بپرس: امروز چه کسی بهتری بودم؟", "author": "دل نوشت", "cat": "شب", "tags": "#شب #حکمت #عرفان", "en": "Before sleeping, ask yourself: who was I better for today?"},
    {"text": "شب‌هایی که نمی‌توانی بخوابی، شاید روحت چیزی برای گفتن دارد.", "author": "دل نوشت", "cat": "شب", "tags": "#شب #حکمت #عرفان", "en": "Nights you can't sleep, perhaps your soul has something to say."},
    {"text": "در دل شب، ستاره‌ها پیدا می‌شوند؛ در دل غم هم، نور پنهان است.", "author": "دل نوشت", "cat": "شب", "tags": "#شب #حکمت #عرفان", "en": "In the heart of night, stars appear; in the heart of sorrow, light is hidden."},
    {"text": "هر شب که می‌خوابی با نسخه‌ای از خودت خداحافظی می‌کنی؛ فردا کسی تازه‌تر بیدار می‌شود.", "author": "دل نوشت", "cat": "شب", "tags": "#شب #حکمت #عرفان", "en": "Every night you sleep, you say goodbye to a version of yourself; tomorrow someone fresher wakes."},
]

quotes_main = [
    # الهی قمشه‌ای
    {"text": "آنچه در آینه نتوان دید، در چشم دیگران توان یافت. نظر دوستان آیینه‌ای صادق‌تر است.", "author": "دکتر الهی قمشه‌ای", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "What cannot be seen in a mirror, can be found in the eyes of others."},
    {"text": "عشق یعنی دیدن خدا در چهره انسان‌ها. هر که این راز را بفهمد، هرگز از انسان نمی‌گریزد.", "author": "دکتر الهی قمشه‌ای", "cat": "عشق", "tags": "#عشق #حکمت", "en": "Love means seeing God in the face of humans."},
    {"text": "دل آدمی خانه خداست، آن را پاک نگه‌دار تا خدا در آن ساکن شود.", "author": "دکتر الهی قمشه‌ای", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "The human heart is God's home; keep it pure so God may dwell within."},
    {"text": "در خاموشی راز هستی نهفته است. آنکه زیاد می‌گوید، کمتر می‌فهمد.", "author": "دکتر الهی قمشه‌ای", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "In silence lies the secret of existence."},
    {"text": "کتاب دریچه‌ای است به سوی روح انسان‌های بزرگ؛ بخوان تا بزرگ شوی.", "author": "دکتر الهی قمشه‌ای", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "A book is a window to the souls of great humans; read to become great."},
    {"text": "زیباترین لحظه زندگی آن است که انسان خود را فراموش کند و در عشق گم شود.", "author": "دکتر الهی قمشه‌ای", "cat": "عشق", "tags": "#عشق #حکمت", "en": "The most beautiful moment in life is when a person forgets themselves and gets lost in love."},
    {"text": "انسان با مرگ تمام نمی‌شود؛ آنچه از انسان می‌ماند، محبتی است که در دل دیگران کاشته.", "author": "دکتر الهی قمشه‌ای", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "A person does not end with death; what remains is the love planted in others' hearts."},
    {"text": "علم بدون عشق سرد است؛ عشق بدون علم کور. باید هر دو را با هم داشت.", "author": "دکتر الهی قمشه‌ای", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Knowledge without love is cold; love without knowledge is blind."},
    # مولانا
    {"text": "بشنو این نی چون شکایت می‌کند، از جدایی‌ها حکایت می‌کند. هر که از یاری جدا افتاد دور، باز جوید روزگار وصل و نور.", "author": "مولانا", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "Listen to the reed, how it tells a tale of separations."},
    {"text": "هر که را اسرار حق آموختند، مهر کردند و دهانش دوختند. راز عارف در سکوت اوست.", "author": "مولانا", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "Whoever was taught the secrets of truth had their mouth sealed with a kiss."},
    {"text": "از کوزه همان برون تراود که در اوست. آدمی هر چه در باطن دارد، در ظاهر نشان می‌دهد.", "author": "مولانا", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "From the jug flows only what is within it."},
    {"text": "عشق آمد عقل را بیگانه کرد. عقل می‌گوید برو، عشق می‌گوید بمان؛ کدام را بشنوی؟", "author": "مولانا", "cat": "عشق", "tags": "#عشق #حکمت", "en": "Love came and made reason a stranger."},
    {"text": "آتش عشق است کاندر نی فتاد. سوختن شیرین است وقتی برای خدا باشد.", "author": "مولانا", "cat": "عشق", "tags": "#عشق #حکمت", "en": "It is the fire of love that has fallen into the reed."},
    {"text": "خاموشی دریای علم است و کلام چون ساحل. عمق دریا را در سکوت می‌یابی.", "author": "مولانا", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "Silence is the sea of knowledge; speech is but its shore."},
    {"text": "در درون هر آدمی جهانی است، کاو به غفلت آن جهان را می‌خورد.", "author": "مولانا", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Within every person is a world, which they devour in heedlessness."},
    {"text": "آدمی دید است و باقی پوست است. دید آن باشد که دید دوست است.", "author": "مولانا", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "A person is vision and the rest is just skin."},
    # حافظ
    {"text": "رسید مژده که ایام غم نخواهد ماند. چنان نماند و چنین هم نخواهد ماند.", "author": "حافظ", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "Good news arrived: the days of sorrow shall not last."},
    {"text": "دلا بسوز که سوز تو کارها بکند. نفس گرم حافظ دل سنگ را آب می‌کند.", "author": "حافظ", "cat": "عشق", "tags": "#عشق #حکمت", "en": "Oh heart, burn! for your burning shall accomplish things."},
    {"text": "بیا که قصر امل سخت سست بنیاد است. بیار باده که بنیاد عمر بر باد است.", "author": "حافظ", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Come, for the palace of hope has a very weak foundation."},
    {"text": "دنیا به کسی وفا نکرد که دل بست. بگذار و بگذر که این رسم دوران است.", "author": "حافظ", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "The world has been faithful to no one who gave their heart to it."},
    {"text": "خوش باش دل که باز آید آنچه رفت. صبر کن ای دل که صبر آسان‌تر از گریه نیست.", "author": "حافظ", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "Be glad, oh heart, for what has gone shall return."},
    {"text": "غم دل با که بگویم که در این دور جهان، مردم چشمم ندیده‌ست کسی دردم را.", "author": "حافظ", "cat": "دل_نوشت", "tags": "#دل_نوشت #احساس", "en": "To whom shall I tell the sorrow of my heart?"},
    # سعدی
    {"text": "بنی آدم اعضای یک پیکرند که در آفرینش ز یک گوهرند. چو عضوی به درد آورد روزگار، دگر عضوها را نماند قرار.", "author": "سعدی", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Human beings are members of a whole, in creation of one essence and soul."},
    {"text": "علم بی عمل چون درخت بی ثمر است. هر که عمل نکند، علمش وبال اوست.", "author": "سعدی", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Knowledge without action is like a tree without fruit."},
    {"text": "تندرستی گنجی است پنهان. قدر آن را بدان پیش از آنکه از دستش بدهی.", "author": "سعدی", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Good health is a hidden treasure."},
    {"text": "هر که نیاموخت از گذشت روزگار، هیچ نیاموزد ز هیچ آموزگار.", "author": "سعدی", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Whoever has not learned from the passage of time, will learn from no teacher."},
    {"text": "آدمی را یک سخن ویران کند، یک سخن هم گمشده را رام کند. زبان در دهان نگه‌دار.", "author": "سعدی", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "One word can destroy a person; one word can also tame a lost soul."},
    # فردوسی
    {"text": "توانا بود هر که دانا بود. ز دانش دل پیر برنا بود. علم بخوان تا جوان بمانی.", "author": "فردوسی", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "Whoever is wise shall be powerful; knowledge keeps the old heart young."},
    {"text": "الهی چنان کن سرانجام کار، تو خشنود باشی و ما رستگار.", "author": "فردوسی", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "O God, arrange the end of our affairs so that You are pleased and we are saved."},
    {"text": "میازار موری که دانه‌کش است، که جان دارد و جان شیرین خوش است.", "author": "فردوسی", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Do not hurt the ant that carries its grain; it has a soul and a soul is precious."},
    {"text": "چو فردا شود فکر فردا کنیم. همین امشب باید که شادی کنیم.", "author": "فردوسی", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "When tomorrow comes, we shall think of tomorrow; tonight we must rejoice."},
    # تولستوی
    {"text": "بشر را محبت کافی است برای رستگاری. همه چیز با محبت حل می‌شود.", "author": "لئو تولستوی", "cat": "عشق", "tags": "#عشق #حکمت", "en": "Love alone is enough for humanity's salvation."},
    {"text": "زندگی کوتاه است، پس آن را با کینه و نفرت تلف مکن. ببخش و آزاد باش.", "author": "لئو تولستوی", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Life is too short to waste on hatred and resentment. Forgive and be free."},
    {"text": "همه می‌خواهند دنیا را تغییر دهند، اما کسی نمی‌خواهد خود را تغییر دهد.", "author": "لئو تولستوی", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Everyone thinks of changing the world, but no one thinks of changing himself."},
    {"text": "مهم‌ترین لحظه همیشه حال است؛ مهم‌ترین کار همین کاری است که الان داری انجام می‌دهی.", "author": "لئو تولستوی", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "The most important moment is always now; the most important task is what you are doing right now."},
    {"text": "عشق واقعی یعنی خواستن خوشبختی دیگری، حتی اگر خوشبختی او بدون تو باشد.", "author": "لئو تولستوی", "cat": "عشق", "tags": "#عشق #حکمت", "en": "True love means wanting the happiness of the other, even if that happiness is without you."},
    {"text": "قوی‌ترین سلاح‌ها عشق و صبر هستند. هیچ دیواری در برابر این دو نمی‌ایستد.", "author": "لئو تولستوی", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "The most powerful weapons are love and patience."},
    # دوستایوفسکی
    {"text": "تنها راه گریز از دیوانگی، عاشق شدن است. دیوانه‌ای که عاشق است، عاقل‌تر از عاقلی است که عاشق نیست.", "author": "فئودور دوستایوفسکی", "cat": "عشق", "tags": "#عشق #حکمت", "en": "The only escape from madness is to fall in love."},
    {"text": "زیبایی جهان را نجات خواهد داد. اما اول باید خودت زیبا باشی.", "author": "فئودور دوستایوفسکی", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Beauty will save the world."},
    {"text": "انسان موجودی است که به همه چیز عادت می‌کند. و شاید این بهترین تعریف اوست.", "author": "فئودور دوستایوفسکی", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Man is a creature that can get used to anything."},
    {"text": "دوست داشتن یعنی دیدن انسان آنگونه که خدا او را آفریده، نه آنگونه که گناه او را ساخته.", "author": "فئودور دوستایوفسکی", "cat": "عشق", "tags": "#عشق #حکمت", "en": "To love someone means to see them as God intended them to be."},
    {"text": "درد را می‌توان کشید؛ خجالت، سخت‌تر است. درد تمام می‌شود، خجالت می‌ماند.", "author": "فئودور دوستایوفسکی", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Pain can be endured; shame is harder. Pain ends; shame remains."},
    # نیچه
    {"text": "آنچه مرا نکشد، قوی‌ترم می‌کند. پس از هر سختی، نسخه‌ای قوی‌تر از خودت متولد می‌شود.", "author": "فریدریش نیچه", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "What does not kill me, makes me stronger."},
    {"text": "انسان چیزی است که باید از آن فراتر رفت. همیشه می‌توانی بیشتر از دیروز باشی.", "author": "فریدریش نیچه", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "Man is something that shall be surpassed."},
    {"text": "بدون موسیقی، زندگی یک اشتباه بود. هنر است که زندگی را تحمل‌پذیر می‌کند.", "author": "فریدریش نیچه", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Without music, life would be a mistake."},
    {"text": "کسی که دلیلی برای زیستن دارد، تقریباً هر چگونه زیستنی را تحمل می‌کند.", "author": "فریدریش نیچه", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "He who has a why to live can bear almost any how."},
    # اینشتین
    {"text": "تخیل مهم‌تر از دانش است. دانش محدود است، اما تخیل دنیا را در بر می‌گیرد.", "author": "آلبرت اینشتین", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "Imagination is more important than knowledge."},
    {"text": "تنها زندگی که ارزش زیستن دارد، زندگی برای دیگران است. خود را در دیگران بیاب.", "author": "آلبرت اینشتین", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Only a life lived for others is a life worthwhile."},
    {"text": "دو چیز بی‌نهایت است: کیهان و حماقت بشر. البته در مورد اولی مطمئن نیستم.", "author": "آلبرت اینشتین", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Two things are infinite: the universe and human stupidity; and I'm not sure about the universe."},
    # فرانکل
    {"text": "همه چیز را می‌توان از انسان گرفت، مگر آزادی انتخاب نگرش در هر شرایطی. این آخرین آزادی توست.", "author": "ویکتور فرانکل", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "Everything can be taken from a man but one thing: the freedom to choose one's attitude."},
    {"text": "کسی که دلیلی برای زندگی دارد، هر چگونه زیستنی را تحمل می‌کند. معنا قوی‌ترین نیروست.", "author": "ویکتور فرانکل", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "He who has a why to live can bear almost any how."},
    {"text": "انسان می‌تواند در هر شرایطی معنا بیابد. حتی در رنج، معنایی پنهان است.", "author": "ویکتور فرانکل", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Man can find meaning in any circumstances."},
    # امام علی
    {"text": "گاهی خاموش ماندن بلیغ‌ترین سخن است. سکوت عاقلانه بهتر از گفتار نادانانه است.", "author": "امام علی (ع)", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Sometimes silence is the most eloquent speech."},
    {"text": "ارزش هر کس به اندازه همت اوست. کوچک فکر کنی کوچک می‌مانی.", "author": "امام علی (ع)", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "The value of every person is equal to their ambition."},
    {"text": "دانش گنجی است که صاحبش را می‌پاید و هیچ دزدی نمی‌تواند آن را بدزدد.", "author": "امام علی (ع)", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Knowledge is a treasure that guards its owner."},
    {"text": "با مردم چنان باش که اگر مردی بر تو بگریند و اگر زیستی مشتاقت باشند.", "author": "امام علی (ع)", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Be with people such that if you die, they weep for you, and if you live, they long for you."},
    {"text": "برادر دینی تو یا گناهت را می‌پوشاند، یا دردت را درمان می‌کند، یا خیری به تو می‌رساند.", "author": "امام علی (ع)", "cat": "حکمت", "tags": "#حکمت #عرفان", "en": "Your true brother either covers your sin, heals your pain, or brings you good."},
    # خواجه عبدالله انصاری
    {"text": "سالک را سه نشانه است: کم خوردن، کم خفتن، کم گفتن. هر که این سه را نگه دارد، به مقصد می‌رسد.", "author": "خواجه عبدالله انصاری", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "The seeker has three signs: eating little, sleeping little, speaking little."},
    {"text": "الهی اگر بهشت را آفریدی برای ما کافی است که تو را می‌شناسیم؛ بهشت کجاست که تو نباشی؟", "author": "خواجه عبدالله انصاری", "cat": "عرفان", "tags": "#عرفان #حکمت", "en": "O God, if You created paradise, it is enough that we know You."},
    # ماندلا
    {"text": "شجاعت یعنی ترسیدن و باز هم قدم برداشتن. قهرمان کسی نیست که نمی‌ترسد؛ کسی است که با ترس پیش می‌رود.", "author": "نلسون ماندلا", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "Courage is not the absence of fear, but the triumph over it."},
    {"text": "آموزش قوی‌ترین سلاحی است که می‌توانی برای تغییر دنیا استفاده کنی.", "author": "نلسون ماندلا", "cat": "انگیزشی", "tags": "#انگیزشی #حکمت", "en": "Education is the most powerful weapon you can use to change the world."},
    # خیام
    {"text": "هر که آمد عمارت نو ساخت، رفت و منزل به دیگری پرداخت. ما هم خواهیم رفت؛ پس چه غمی؟", "author": "عمر خیام", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Whoever came built a new dwelling, left and gave it to another."},
    {"text": "این قافله عمر عجب می‌گذرد. دریاب که این کاروان می‌گذرد. لحظه را غنیمت شمار.", "author": "عمر خیام", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "This caravan of life passes strangely; seize the moment, for this caravan is passing."},
    {"text": "می خور که عقل را این سخن خوش آید. آنچه در دل داری بگو؛ که امروز فرصت است.", "author": "عمر خیام", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Drink, for reason approves of this saying."},
    # اریک فروم
    {"text": "زندگی یک هنر است، و مثل هر هنری باید تمرین کرد. هیچ‌کس با هنر زندگی به دنیا نمی‌آید.", "author": "اریک فروم", "cat": "فلسفه", "tags": "#فلسفه #حکمت", "en": "Life is an art, and like any art it must be practiced."},
    {"text": "عشق تنها پاسخ معقول به مسئله وجود انسان است. بدون عشق، وجود پوچ است.", "author": "اریک فروم", "cat": "عشق", "tags": "#عشق #حکمت", "en": "Love is the only sane and satisfactory answer to the problem of human existence."},
    # دل نوشت‌های جدید
    {"text": "گاهی تنها ماندن نشانه رشد است، نه شکست. آدم‌های کوچک در جمع زندگی می‌کنند، بزرگ‌ها در خلوت رشد می‌کنند.", "author": "دل نوشت", "cat": "دل_نوشت", "tags": "#دل_نوشت #احساس", "en": "Sometimes being alone is a sign of growth, not failure."},
    {"text": "اگر همه رفتند، شاید وقت آن رسیده که با خودت بمانی. شاید خودت بهترین همراه توی.", "author": "دل نوشت", "cat": "دل_نوشت", "tags": "#دل_نوشت #احساس", "en": "If everyone left, perhaps it's time to stay with yourself."},
    {"text": "درد هم معلم است، اگر بگذاری درس بدهد. هر دردی پیامی دارد؛ گوش کن.", "author": "دل نوشت", "cat": "دل_نوشت", "tags": "#دل_نوشت #احساس", "en": "Pain is also a teacher, if you let it teach."},
    {"text": "بعضی آدم‌ها برای یاد دادن می‌آیند، نه برای ماندن. وقتی رفتند، به جای گریه، از درسشان ممنون باش.", "author": "دل نوشت", "cat": "دل_نوشت", "tags": "#دل_نوشت #احساس", "en": "Some people come to teach, not to stay."},
    {"text": "هر چیزی که از دست می‌دهی، اگر صبر کنی، جایش را چیز بهتری می‌گیرد. صبر کن.", "author": "دل نوشت", "cat": "دل_نوشت", "tags": "#دل_نوشت #احساس", "en": "Everything you lose, if you are patient, will be replaced by something better."},
    {"text": "سکوتت گاهی بلندتر از هر فریادی است. نه همه چیز را باید توضیح داد.", "author": "دل نوشت", "cat": "دل_نوشت", "tags": "#دل_نوشت #احساس", "en": "Your silence is sometimes louder than any cry."},
    {"text": "آدم وقتی می‌شکند، تازه می‌فهمد از چه ساخته شده. شکستن شرط شناختن خود است.", "author": "دل نوشت", "cat": "دل_نوشت", "tags": "#دل_نوشت #احساس", "en": "When a person breaks, they finally understand 
