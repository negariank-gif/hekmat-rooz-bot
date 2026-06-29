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
    {"text": "هر صبح که چشم می‌گشایی، هدیه‌ای تازه از خداست. از این هدیه قدردانی کن.", "author": "دکتر الهی قمشه‌ای", "cat": "صبح", "en": "Every morning you open your eyes is a fresh gift from God."},
    {"text": "صبح را با شکرگزاری آغاز کن؛ روزی که با سپاس شروع شود، با برکت پایان می‌یابد.", "author": "دل نوشت", "cat": "صبح", "en": "Start the morning with gratitude; a day that begins with thanks ends with blessings."},
    {"text": "هر سپیده‌دم فرصتی است که دیروز نداشتی؛ غنیمت بشمارش.", "author": "دل نوشت", "cat": "صبح", "en": "Every dawn is an opportunity you didn't have yesterday; treasure it."},
    {"text": "صبح اول دوست خود باش، بعد به دنبال دوست دیگر برو.", "author": "دل نوشت", "cat": "صبح", "en": "In the morning, first be your own friend, then seek others."},
    {"text": "با طلوع آفتاب، امید تازه‌ای در دل بکار؛ که هر روز بذر جدیدی است.", "author": "دل نوشت", "cat": "صبح", "en": "With the sunrise, plant fresh hope in your heart; every day is a new seed."},
]

quotes_night = [
    {"text": "شب که می‌شود، دل می‌خواهد سکوت؛ که در سکوت، خدا سخن می‌گوید.", "author": "دل نوشت", "cat": "شب", "en": "When night comes, the heart craves silence; for in silence, God speaks."},
    {"text": "پیش از خواب از خود بپرس: امروز چه کسی بهتری بودم؟", "author": "دل نوشت", "cat": "شب", "en": "Before sleeping, ask yourself: who was I better for today?"},
    {"text": "شب‌هایی که نمی‌توانی بخوابی، شاید روحت چیزی برای گفتن دارد.", "author": "دل نوشت", "cat": "شب", "en": "Nights you can't sleep, perhaps your soul has something to say."},
    {"text": "در دل شب، ستاره‌ها پیدا می‌شوند؛ در دل غم هم، نور پنهان است.", "author": "دل نوشت", "cat": "شب", "en": "In the heart of night, stars appear; in the heart of sorrow, light is hidden."},
    {"text": "هر شب که می‌خوابی با نسخه‌ای از خودت خداحافظی می‌کنی؛ فردا کسی تازه‌تر بیدار می‌شود.", "author": "دل نوشت", "cat": "شب", "en": "Every night you sleep, you say goodbye to a version of yourself; tomorrow someone fresher wakes."},
]

quotes_main = [
    # الهی قمشه‌ای
    {"text": "آنچه در آینه نتوان دید، در چشم دیگران توان یافت. نظر دوستان آیینه‌ای صادق‌تر است.", "author": "دکتر الهی قمشه‌ای", "cat": "حکمت", "en": "What cannot be seen in a mirror, can be found in the eyes of others."},
    {"text": "عشق یعنی دیدن خدا در چهره انسان‌ها. هر که این راز را بفهمد، هرگز از انسان نمی‌گریزد.", "author": "دکتر الهی قمشه‌ای", "cat": "عشق", "en": "Love means seeing God in the face of humans."},
    {"text": "دل آدمی خانه خداست، آن را پاک نگه‌دار تا خدا در آن ساکن شود.", "author": "دکتر الهی قمشه‌ای", "cat": "عرفان", "en": "The human heart is God's home; keep it pure so God may dwell within."},
    {"text": "در خاموشی راز هستی نهفته است. آنکه زیاد می‌گوید، کمتر می‌فهمد.", "author": "دکتر الهی قمشه‌ای", "cat": "عرفان", "en": "In silence lies the secret of existence."},
    {"text": "کتاب دریچه‌ای است به سوی روح انسان‌های بزرگ؛ بخوان تا بزرگ شوی.", "author": "دکتر الهی قمشه‌ای", "cat": "حکمت", "en": "A book is a window to the souls of great humans; read to become great."},
    {"text": "زیباترین لحظه زندگی آن است که انسان خود را فراموش کند و در عشق گم شود.", "author": "دکتر الهی قمشه‌ای", "cat": "عشق", "en": "The most beautiful moment in life is when a person forgets themselves and gets lost in love."},
    {"text": "انسان با مرگ تمام نمی‌شود؛ آنچه از انسان می‌ماند، محبتی است که در دل دیگران کاشته.", "author": "دکتر الهی قمشه‌ای", "cat": "عرفان", "en": "A person does not end with death; what remains is the love planted in others' hearts."},
    {"text": "علم بدون عشق سرد است؛ عشق بدون علم کور. باید هر دو را با هم داشت.", "author": "دکتر الهی قمشه‌ای", "cat": "حکمت", "en": "Knowledge without love is cold; love without knowledge is blind."},
    # مولانا
    {"text": "بشنو این نی چون شکایت می‌کند، از جدایی‌ها حکایت می‌کند. هر که از یاری جدا افتاد دور، باز جوید روزگار وصل و نور.", "author": "مولانا", "cat": "عرفان", "en": "Listen to the reed, how it tells a tale of separations."},
    {"text": "هر که را اسرار حق آموختند، مهر کردند و دهانش دوختند. راز عارف در سکوت اوست.", "author": "مولانا", "cat": "عرفان", "en": "Whoever was taught the secrets of truth had their mouth sealed with a kiss."},
    {"text": "از کوزه همان برون تراود که در اوست. آدمی هر چه در باطن دارد، در ظاهر نشان می‌دهد.", "author": "مولانا", "cat": "حکمت", "en": "From the jug flows only what is within it."},
    {"text": "عشق آمد عقل را بیگانه کرد. عقل می‌گوید برو، عشق می‌گوید بمان؛ کدام را بشنوی؟", "author": "مولانا", "cat": "عشق", "en": "Love came and made reason a stranger."},
    {"text": "آتش عشق است کاندر نی فتاد. سوختن شیرین است وقتی برای خدا باشد.", "author": "مولانا", "cat": "عشق", "en": "It is the fire of love that has fallen into the reed."},
    {"text": "خاموشی دریای علم است و کلام چون ساحل. عمق دریا را در سکوت می‌یابی.", "author": "مولانا", "cat": "عرفان", "en": "Silence is the sea of knowledge; speech is but its shore."},
    {"text": "در درون هر آدمی جهانی است، کاو به غفلت آن جهان را می‌خورد.", "author": "مولانا", "cat": "فلسفه", "en": "Within every person is a world, which they devour in heedlessness."},
    {"text": "آدمی دید است و باقی پوست است. دید آن باشد که دید دوست است.", "author": "مولانا", "cat": "عرفان", "en": "A person is vision and the rest is just skin."},
    # حافظ
    {"text": "رسید مژده که ایام غم نخواهد ماند. چنان نماند و چنین هم نخواهد ماند.", "author": "حافظ", "cat": "انگیزشی", "en": "Good news arrived: the days of sorrow shall not last."},
    {"text": "دلا بسوز که سوز تو کارها بکند. نفس گرم حافظ دل سنگ را آب می‌کند.", "author": "حافظ", "cat": "عشق", "en": "Oh heart, burn! for your burning shall accomplish things."},
    {"text": "بیا که قصر امل سخت سست بنیاد است. بیار باده که بنیاد عمر بر باد است.", "author": "حافظ", "cat": "فلسفه", "en": "Come, for the palace of hope has a very weak foundation."},
    {"text": "دنیا به کسی وفا نکرد که دل بست. بگذار و بگذر که این رسم دوران است.", "author": "حافظ", "cat": "حکمت", "en": "The world has been faithful to no one who gave their heart to it."},
    {"text": "خوش باش دل که باز آید آنچه رفت. صبر کن ای دل که صبر آسان‌تر از گریه نیست.", "author": "حافظ", "cat": "انگیزشی", "en": "Be glad, oh heart, for what has gone shall return."},
    {"text": "غم دل با که بگویم که در این دور جهان، مردم چشمم ندیده‌ست کسی دردم را.", "author": "حافظ", "cat": "دل_نوشت", "en": "To whom shall I tell the sorrow of my heart?"},
    # سعدی
    {"text": "بنی آدم اعضای یک پیکرند که در آفرینش ز یک گوهرند. چو عضوی به درد آورد روزگار، دگر عضوها را نماند قرار.", "author": "سعدی", "cat": "حکمت", "en": "Human beings are members of a whole, in creation of one essence and soul."},
    {"text": "علم بی عمل چون درخت بی ثمر است. هر که عمل نکند، علمش وبال اوست.", "author": "سعدی", "cat": "حکمت", "en": "Knowledge without action is like a tree without fruit."},
    {"text": "تندرستی گنجی است پنهان. قدر آن را بدان پیش از آنکه از دستش بدهی.", "author": "سعدی", "cat": "حکمت", "en": "Good health is a hidden treasure."},
    {"text": "هر که نیاموخت از گذشت روزگار، هیچ نیاموزد ز هیچ آموزگار.", "author": "سعدی", "cat": "حکمت", "en": "Whoever has not learned from the passage of time, will learn from no teacher."},
    {"text": "آدمی را یک سخن ویران کند، یک سخن هم گمشده را رام کند. زبان در دهان نگه‌دار.", "author": "سعدی", "cat": "حکمت", "en": "One word can destroy a person; one word can also tame a lost soul."},
    # فردوسی
    {"text": "توانا بود هر که دانا بود. ز دانش دل پیر برنا بود. علم بخوان تا جوان بمانی.", "author": "فردوسی", "cat": "انگیزشی", "en": "Whoever is wise shall be powerful; knowledge keeps the old heart young."},
    {"text": "الهی چنان کن سرانجام کار، تو خشنود باشی و ما رستگار.", "author": "فردوسی", "cat": "عرفان", "en": "O God, arrange the end of our affairs so that You are pleased and we are saved."},
    {"text": "میازار موری که دانه‌کش است، که جان دارد و جان شیرین خوش است.", "author": "فردوسی", "cat": "حکمت", "en": "Do not hurt the ant that carries its grain; it has a soul and a soul is precious."},
    {"text": "چو فردا شود فکر فردا کنیم. همین امشب باید که شادی کنیم.", "author": "فردوسی", "cat": "فلسفه", "en": "When tomorrow comes, we shall think of tomorrow; tonight we must rejoice."},
    # تولستوی
    {"text": "بشر را محبت کافی است برای رستگاری. همه چیز با محبت حل می‌شود.", "author": "لئو تولستوی", "cat": "عشق", "en": "Love alone is enough for humanity's salvation."},
    {"text": "زندگی کوتاه است، پس آن را با کینه و نفرت تلف مکن. ببخش و آزاد باش.", "author": "لئو تولستوی", "cat": "حکمت", "en": "Life is too short to waste on hatred and resentment. Forgive and be free."},
    {"text": "همه می‌خواهند دنیا را تغییر دهند، اما کسی نمی‌خواهد خود را تغییر دهد.", "author": "لئو تولستوی", "cat": "فلسفه", "en": "Everyone thinks of changing the world, but no one thinks of changing himself."},
    {"text": "مهم‌ترین لحظه همیشه حال است؛ مهم‌ترین کار همین کاری است که الان داری انجام می‌دهی.", "author": "لئو تولستوی", "cat": "انگیزشی", "en": "The most important moment is always now; the most important task is what you are doing right now."},
    {"text": "عشق واقعی یعنی خواستن خوشبختی دیگری، حتی اگر خوشبختی او بدون تو باشد.", "author": "لئو تولستوی", "cat": "عشق", "en": "True love means wanting the happiness of the other, even if that happiness is without you."},
    {"text": "قوی‌ترین سلاح‌ها عشق و صبر هستند. هیچ دیواری در برابر این دو نمی‌ایستد.", "author": "لئو تولستوی", "cat": "انگیزشی", "en": "The most powerful weapons are love and patience."},
    # دوستایوفسکی
    {"text": "تنها راه گریز از دیوانگی، عاشق شدن است. دیوانه‌ای که عاشق است، عاقل‌تر از عاقلی است که عاشق نیست.", "author": "فئودور دوستایوفسکی", "cat": "عشق", "en": "The only escape from madness is to fall in love."},
    {"text": "زیبایی جهان را نجات خواهد داد. اما اول باید خودت زیبا باشی.", "author": "فئودور دوستایوفسکی", "cat": "فلسفه", "en": "Beauty will save the world."},
    {"text": "انسان موجودی است که به همه چیز عادت می‌کند. و شاید این بهترین تعریف اوست.", "author": "فئودور دوستایوفسکی", "cat": "فلسفه", "en": "Man is a creature that can get used to anything."},
    {"text": "دوست داشتن یعنی دیدن انسان آنگونه که خدا او را آفریده، نه آنگونه که گناه او را ساخته.", "author": "فئودور دوستایوفسکی", "cat": "عشق", "en": "To love someone means to see them as God intended them to be."},
    {"text": "درد را می‌توان کشید؛ خجالت، سخت‌تر است. درد تمام می‌شود، خجالت می‌ماند.", "author": "فئودور دوستایوفسکی", "cat": "فلسفه", "en": "Pain can be endured; shame is harder. Pain ends; shame remains."},
    # نیچه
    {"text": "آنچه مرا نکشد، قوی‌ترم می‌کند. پس از هر سختی، نسخه‌ای قوی‌تر از خودت متولد می‌شود.", "author": "فریدریش نیچه", "cat": "انگیزشی", "en": "What does not kill me, makes me stronger."},
    {"text": "انسان چیزی است که باید از آن فراتر رفت. همیشه می‌توانی بیشتر از دیروز باشی.", "author": "فریدریش نیچه", "cat": "انگیزشی", "en": "Man is something that shall be surpassed."},
    {"text": "بدون موسیقی، زندگی یک اشتباه بود. هنر است که زندگی را تحمل‌پذیر می‌کند.", "author": "فریدریش نیچه", "cat": "فلسفه", "en": "Without music, life would be a mistake."},
    {"text": "کسی که دلیلی برای زیستن دارد، تقریباً هر چگونه زیستنی را تحمل می‌کند.", "author": "فریدریش نیچه", "cat": "انگیزشی", "en": "He who has a why to live can bear almost any how."},
    # اینشتین
    {"text": "تخیل مهم‌تر از دانش است. دانش محدود است، اما تخیل دنیا را در بر می‌گیرد.", "author": "آلبرت اینشتین", "cat": "انگیزشی", "en": "Imagination is more important than knowledge."},
    {"text": "تنها زندگی که ارزش زیستن دارد، زندگی برای دیگران است. خود را در دیگران بیاب.", "author": "آلبرت اینشتین", "cat": "حکمت", "en": "Only a life lived for others is a life worthwhile."},
    {"text": "دو چیز بی‌نهایت است: کیهان و حماقت بشر. البته در مورد اولی مطمئن نیستم.", "author": "آلبرت اینشتین", "cat": "فلسفه", "en": "Two things are infinite: the universe and human stupidity; and I'm not sure about the universe."},
    # فرانکل
    {"text": "همه چیز را می‌توان از انسان گرفت، مگر آزادی انتخاب نگرش در هر شرایطی. این آخرین آزادی توست.", "author": "ویکتور فرانکل", "cat": "انگیزشی", "en": "Everything can be taken from a man but one thing: the freedom to choose one's attitude."},
    {"text": "کسی که دلیلی برای زندگی دارد، هر چگونه زیستنی را تحمل می‌کند. معنا قوی‌ترین نیروست.", "author": "ویکتور فرانکل", "cat": "انگیزشی", "en": "He who has a why to live can bear almost any how."},
    {"text": "انسان می‌تواند در هر شرایطی معنا بیابد. حتی در رنج، معنایی پنهان است.", "author": "ویکتور فرانکل", "cat": "فلسفه", "en": "Man can find meaning in any circumstances."},
    # امام علی
    {"text": "گاهی خاموش ماندن بلیغ‌ترین سخن است. سکوت عاقلانه بهتر از گفتار نادانانه است.", "author": "امام علی (ع)", "cat": "حکمت", "en": "Sometimes silence is the most eloquent speech."},
    {"text": "ارزش هر کس به اندازه همت اوست. کوچک فکر کنی کوچک می‌مانی.", "author": "امام علی (ع)", "cat": "انگیزشی", "en": "The value of every person is equal to their ambition."},
    {"text": "دانش گنجی است که صاحبش را می‌پاید و هیچ دزدی نمی‌تواند آن را بدزدد.", "author": "امام علی (ع)", "cat": "حکمت", "en": "Knowledge is a treasure that guards its owner."},
    {"text": "با مردم چنان باش که اگر مردی بر تو بگریند و اگر زیستی مشتاقت باشند.", "author": "امام علی (ع)", "cat": "حکمت", "en": "Be with people such that if you die, they weep for you, and if you live, they long for you."},
    {"text": "برادر دینی تو یا گناهت را می‌پوشاند، یا دردت را درمان می‌کند، یا خیری به تو می‌رساند.", "author": "امام علی (ع)", "cat": "حکمت", "en": "Your true brother either covers your sin, heals your pain, or brings you good."},
    # خواجه عبدالله انصاری
    {"text": "سالک را سه نشانه است: کم خوردن، کم خفتن، کم گفتن. هر که این سه را نگه دارد، به مقصد می‌رسد.", "author": "خواجه عبدالله انصاری", "cat": "عرفان", "en": "The seeker has three signs: eating little, sleeping little, speaking little."},
    {"text": "الهی اگر بهشت را آفریدی برای ما کافی است که تو را می‌شناسیم؛ بهشت کجاست که تو نباشی؟", "author": "خواجه عبدالله انصاری", "cat": "عرفان", "en": "O God, if You created paradise, it is enough that we know You."},
    # ماندلا
    {"text": "شجاعت یعنی ترسیدن و باز هم قدم برداشتن. قهرمان کسی نیست که نمی‌ترسد؛ کسی است که با ترس پیش می‌رود.", "author": "نلسون ماندلا", "cat": "انگیزشی", "en": "Courage is not the absence of fear, but the triumph over it."},
    {"text": "آموزش قوی‌ترین سلاحی است که می‌توانی برای تغییر دنیا استفاده کنی.", "author": "نلسون ماندلا", "cat": "انگیزشی", "en": "Education is the most powerful weapon you can use to change the world."},
    # خیام
    {"text": "هر که آمد عمارت نو ساخت، رفت و منزل به دیگری پرداخت. ما هم خواهیم رفت؛ پس چه غمی؟", "author": "عمر خیام", "cat": "فلسفه", "en": "Whoever came built a new dwelling, left and gave it to another."},
    {"text": "این قافله عمر عجب می‌گذرد. دریاب که این کاروان می‌گذرد. لحظه را غنیمت شمار.", "author": "عمر خیام", "cat": "فلسفه", "en": "This caravan of life passes strangely; seize the moment, for this caravan is passing."},
    {"text": "می خور که عقل را این سخن خوش آید. آنچه در دل داری بگو؛ که امروز فرصت است.", "author": "عمر خیام", "cat": "فلسفه", "en": "Drink, for reason approves of this saying."},
    # اریک فروم
    {"text": "زندگی یک هنر است، و مثل هر هنری باید تمرین کرد. هیچ‌کس با هنر زندگی به دنیا نمی‌آید.", "author": "اریک فروم", "cat": "فلسفه", "en": "Life is an art, and like any art it must be practiced."},
    {"text": "عشق تنها پاسخ معقول به مسئله وجود انسان است. بدون عشق، وجود پوچ است.", "author": "اریک فروم", "cat": "عشق", "en": "Love is the only sane and satisfactory answer to the problem of human existence."},
    # دل نوشت‌های جدید
    {"text": "گاهی تنها ماندن نشانه رشد است، نه شکست. آدم‌های کوچک در جمع زندگی می‌کنند، بزرگ‌ها در خلوت رشد می‌کنند.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Sometimes being alone is a sign of growth, not failure."},
    {"text": "اگر همه رفتند، شاید وقت آن رسیده که با خودت بمانی. شاید خودت بهترین همراه توی.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "If everyone left, perhaps it's time to stay with yourself."},
    {"text": "درد هم معلم است، اگر بگذاری درس بدهد. هر دردی پیامی دارد؛ گوش کن.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Pain is also a teacher, if you let it teach."},
    {"text": "بعضی آدم‌ها برای یاد دادن می‌آیند، نه برای ماندن. وقتی رفتند، به جای گریه، از درسشان ممنون باش.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Some people come to teach, not to stay."},
    {"text": "هر چیزی که از دست می‌دهی، اگر صبر کنی، جایش را چیز بهتری می‌گیرد. صبر کن.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Everything you lose, if you are patient, will be replaced by something better."},
    {"text": "سکوتت گاهی بلندتر از هر فریادی است. نه همه چیز را باید توضیح داد.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Your silence is sometimes louder than any cry."},
    {"text": "آدم وقتی می‌شکند، تازه می‌فهمد از چه ساخته شده. شکستن شرط شناختن خود است.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "When a person breaks, they finally understand what they are made of."},
    {"text": "وقتی همه در می‌روند، خدا می‌ماند. و شاید همین رفتن‌ها برای رسیدن به خدا بود.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "When everyone leaves, God remains."},
    {"text": "بعضی زخم‌ها برای همیشه نمی‌مانند؛ فقط جایشان می‌ماند تا یادت بیاید که زنده بودی.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Some wounds don't last forever; only their scars remain to remind you that you lived."},
    {"text": "در دل هر انسانی چراغی است؛ عشق آن را روشن می‌کند و غرور آن را خاموش.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "In every person's heart is a lamp; love lights it and pride extinguishes it."},
    {"text": "تنهایی عذاب نیست اگر با خودت باشی. عذاب آن است که در جمع هم تنها باشی.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Loneliness is not torment if you are with yourself."},
    {"text": "گاهی باید بگذاری بروند تا بفهمی چه داشتی. ولی وقتی فهمیدی، دیگر نگران نباش.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Sometimes you must let them go to understand what you had."},
    {"text": "ریشه درخت را نمی‌بینی ولی می‌دانی هست؛ ایمان هم همین است. نادیدنی اما حامل همه چیز.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "You can't see the roots of a tree, but you know they're there; faith is the same."},
    {"text": "دنیا آینه است؛ هرچه در آن ببینی بازتاب درون توست. خود را اصلاح کن، دنیا درست می‌شود.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "The world is a mirror; what you see in it reflects your inner self."},
    {"text": "قلب هر انسانی کتابی است؛ بخوانش. اما اول یاد بگیر چطور کتاب بخوانی.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Every person's heart is a book; read it."},
    {"text": "کسی که امروز را دوست دارد، نگران فردا نیست. حال را زندگی کن.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "One who loves today is not worried about tomorrow."},
    {"text": "وقتی دیگر نمی‌توانی ادامه دهی، به یاد بیاور چرا شروع کردی. شروع تو همیشه قوی‌تر از خستگی توست.", "author": "دل نوشت", "cat": "انگیزشی", "en": "When you can no longer continue, remember why you started."},
    {"text": "خواندن یعنی سفر بدون ترک خانه. هر کتاب دنیایی است که به روی تو باز می‌شود.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Reading means traveling without leaving home."},
    {"text": "هر کتابی که می‌خوانی بخشی از تو می‌شود. پس مراقب باش چه می‌خوانی.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Every book you read becomes a part of you."},
    {"text": "کتاب‌ها آینه‌ای هستند که ما را با خودمان روبرو می‌کنند. از این رو‌برویی نترس.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Books are mirrors that confront us with ourselves."},
    {"text": "وقتی گم می‌شوی، کتاب بخوان تا خودت را پیدا کنی. صفحات کتاب نقشه راه بازگشت به خود هستند.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "When you are lost, read a book to find yourself."},
    # رومی
    {"text": "سکوت زبان عاشقان است. وقتی زبان از گفتن عاجز است، دل شروع به سخن می‌کند.", "author": "جلال‌الدین رومی", "cat": "عشق", "en": "Silence is the language of lovers."},
    {"text": "تو را من چشم در راهم، شباهنگام که می‌دانم پگاه از پی شب تاریک می‌آید.", "author": "جلال‌الدین رومی", "cat": "عشق", "en": "I await you; I know that after the dark night, dawn will come."},
    {"text": "درد عشق را دارویی نیست الا وصال. و وصال را پایانی نیست الا کمال.", "author": "جلال‌الدین رومی", "cat": "عشق", "en": "The pain of love has no remedy but union."},
    {"text": "جان من جان جهانم می‌کند. عشق در جانم نهانم می‌کند.", "author": "جلال‌الدین رومی", "cat": "عشق", "en": "My soul makes me the soul of the world; love hides within my soul."},
    # مارکوس اورلیوس
    {"text": "ذهن خود را پاک نگه‌دار. آلودگی ذهن بدتر از آلودگی جسم است.", "author": "مارکوس اورلیوس", "cat": "فلسفه", "en": "Keep your mind clean; mental pollution is worse than physical."},
    {"text": "آنچه در توان داری بکن، با آنچه داری، آنجا که هستی.", "author": "مارکوس اورلیوس", "cat": "انگیزشی", "en": "Do what you can, with what you have, where you are."},
    {"text": "بهترین انتقام، متفاوت بودن از کسی است که به تو آسیب زد.", "author": "مارکوس اورلیوس", "cat": "حکمت", "en": "The best revenge is to be unlike the one who harmed you."},
    # سقراط
    {"text": "من می‌دانم که هیچ نمی‌دانم. این اولین قدم به سوی دانستن است.", "author": "سقراط", "cat": "فلسفه", "en": "I know that I know nothing; this is the first step toward knowing."},
    {"text": "زندگی بدون ارزیابی ارزش زیستن ندارد. هر شب از خود بپرس: امروز چه کردم؟", "author": "سقراط", "cat": "فلسفه", "en": "The unexamined life is not worth living."},
    # ابوعلی سینا
    {"text": "دل را به علم و دانش بساز که علم نور است و جهل تاریکی.", "author": "ابوعلی سینا", "cat": "حکمت", "en": "Build your heart with knowledge; knowledge is light and ignorance is darkness."},
    {"text": "درمان بیشتر بیماری‌ها در خود ماست؛ صبر، آرامش و امید بهترین داروهایند.", "author": "ابوعلی سینا", "cat": "حکمت", "en": "The cure for most ailments is within us; patience, calm, and hope are the best medicines."},
    # ناپلئون هیل
    {"text": "آنچه ذهن می‌تواند تصور کند و به آن ایمان آورد، می‌تواند به دست آورد.", "author": "ناپلئون هیل", "cat": "انگیزشی", "en": "Whatever the mind can conceive and believe, it can achieve."},
    # پائولو کوئلیو
    {"text": "وقتی چیزی را از ته دل بخواهی، تمام کیهان دست به دست هم می‌دهد تا به آن برسی.", "author": "پائولو کوئلیو", "cat": "انگیزشی", "en": "When you want something, all the universe conspires in helping you to achieve it."},
    {"text": "پیش از رسیدن به رویا، باید از همه چیزی که داری دست بکشی.", "author": "پائولو کوئلیو", "cat": "انگیزشی", "en": "Before a dream is realized, you must give up everything you have."},
    # رابیندرانات تاگور
    {"text": "من خواب دیدم که زندگی شادی است. بیدار شدم و دیدم زندگی خدمت است. خدمت کردم و دیدم که خدمت شادی است.", "author": "رابیندرانات تاگور", "cat": "حکمت", "en": "I dreamed that life was joy. I woke and saw that life was service. I served and saw that service was joy."},
    # مادر ترزا
    {"text": "اگر به همه انسان‌ها محبت نمی‌کنی، حداقل به یک نفر آسیب نزن.", "author": "مادر ترزا", "cat": "حکمت", "en": "If you can't love everyone, at least don't hurt anyone."},
    {"text": "ما همه می‌توانیم کارهای بزرگ انجام دهیم. ولی اگر با محبت کوچک عمل کنیم، دنیا عوض می‌شود.", "author": "مادر ترزا", "cat": "حکمت", "en": "We can do no great things; only small things with great love."},
    # احادیث و روایات
    {"text": "هر کس خود را بشناسد، خدا را شناخته است. خودشناسی آغاز خداشناسی است.", "author": "حکمت اسلامی", "cat": "عرفان", "en": "Whoever knows himself, knows God."},
    {"text": "به کسی که به تو بدی کرده نیکی کن؛ که این نه ضعف، بلکه قدرت است.", "author": "حکمت اسلامی", "cat": "حکمت", "en": "Do good to one who has done evil to you; this is not weakness, but strength."},
    # جملات فلسفی جدید
    {"text": "زندگی همان است که در فاصله برنامه‌ریزی‌های ما اتفاق می‌افتد. پس لحظه را دریاب.", "author": "دل نوشت", "cat": "فلسفه", "en": "Life is what happens in the gaps between our plans."},
    {"text": "خوشبخت نیست آن که همه چیز دارد، خوشبخت است آن که از آنچه دارد راضی است.", "author": "دل نوشت", "cat": "حکمت", "en": "Happy is not the one who has everything, but the one who is satisfied with what they have."},
    {"text": "گاهی سخت‌ترین کار، رها کردن چیزی است که قرار بود خوب باشد ولی نشد.", "author": "دل نوشت", "cat": "دل_نوشت", "en": "Sometimes the hardest thing is letting go of something that was supposed to be good."},
    {"text": "آنچه را که نمی‌توانی تغییر دهی، بپذیر. آنچه را که می‌توانی، تغییر بده. و حکمت داشته باش که تفاوت را بدانی.", "author": "دل نوشت", "cat": "حکمت", "en": "Accept what you cannot change; change what you can; and have the wisdom to know the difference."},
    {"text": "بهترین سرمایه‌گذاری، سرمایه‌گذاری بر روی خودت است. هیچ بازدهی بالاتری وجود ندارد.", "author": "دل نوشت", "cat": "انگیزشی", "en": "The best investment is investing in yourself."},
]

all_quotes = quotes_main

def get_time_based_quotes():
    now = datetime.datetime.utcnow()
    iran_hour = (now.hour + 3) % 24
    if iran_hour < 10:
        return quotes_morning
    elif iran_hour >= 21:
        return quotes_night
    else:
        return all_quotes

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

def create_image(quote_text, author, cat):
    width, height = 1080, 1080
    cat_info = CATEGORIES.get(cat, CATEGORIES["حکمت"])
    icon = cat_info["icon"]

    img = create_gradient(width, height, cat_info["color1"], cat_info["color2"])
    draw = ImageDraw.Draw(img)

    # خطوط تزئینی
    draw.rectangle([(60, 60), (width-60, 65)], fill=(255, 215, 0))
    draw.rectangle([(60, height-65), (width-60, height-60)], fill=(255, 215, 0))
    draw.rectangle([(60, 60), (65, height-60)], fill=(255, 215, 0))
    draw.rectangle([(width-65, 60), (width-60, height-60)], fill=(255, 215, 0))

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_large = ImageFont.load_default()
        font_normal = font_large
        font_author = font_large
        font_small = font_large

    # آیکون دسته
    draw.text((width//2, 130), icon, font=font_large, fill=(255, 215, 0), anchor="mm")

    # شکستن متن به خطوط
    words = quote_text.split()
    lines = []
    current_line = ""
    max_chars = 22
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += (" " + word if current_line else word)
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # رسم متن - خط اول بزرگ‌تر
    line_height_large = 72
    line_height_normal = 56
    total_h = line_height_large + (len(lines)-1) * line_height_normal if lines else 0
    start_y = (height - total_h) // 2 - 20

    for i, line in enumerate(lines):
        if i == 0:
            font = font_large
            y = start_y
        else:
            font = font_normal
            y = start_y + line_height_large + (i-1) * line_height_normal

        draw.text((width//2, y), line, font=font, fill=(255, 255, 255), anchor="mm")

    # خط جداکننده
    sep_y = start_y + line_height_large + (len(lines)-1) * line_height_normal + 35
    draw.rectangle([(width//2 - 100, sep_y), (width//2 + 100, sep_y + 3)], fill=(255, 215, 0))

    # نام نویسنده
    draw.text((width//2, sep_y + 45), f"— {author}", font=font_author, fill=(255, 215, 0), anchor="mm")

    # نام کانال
    draw.text((width//2, height - 95), "@sanchobook", font=font_small, fill=(180, 180, 180), anchor="mm")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def send_quote():
    pool = get_time_based_quotes()
    quote = random.choice(pool)

    img_bytes = create_image(quote['text'], quote['author'], quote['cat'])

    en_text = quote.get('en', '')
    caption = (
        f"<i>{quote['text']}</i>\n\n"
        f"— <b>{quote['author']}</b>\n\n"
    )
    if en_text:
        caption += f"<i>{en_text}</i>\n\n"
    caption += f"{quote['tags']} #حکمت #عرفان"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    response = requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "caption": caption,
        "parse_mode": "HTML"
    }, files={"photo": ("quote.png", img_bytes, "image/png")})

    if response.status_code == 200:
        print(f"ارسال شد: {quote['author']} - {quote['cat']}")
    else:
        print(f"خطا: {response.text}")

if __name__ == "__main__":
    send_quote()
