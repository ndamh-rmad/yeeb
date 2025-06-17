import logging
import asyncio
import json
from telegram import Bot, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import aiohttp

with open("bot_config.json", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = "ضع_توكن_البوت_هنا"
CHANNEL_ID = config["channel_username"]
CAPTION_TEMPLATE = config["caption_template"]

SURAHS = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
    "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف", "مريم", "طه",
    "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
    "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص", "الزمر", "غافر",
    "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح", "الحجرات", "ق",
    "الذاريات", "الطور", "النجم", "القمر", "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
    "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
    "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس",
    "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
    "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
    "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر",
    "المسد", "الإخلاص", "الفلق", "الناس"
]

current_index = 0
sent_count = 0

async def send_surah():
    global current_index, sent_count
    surah_name = SURAHS[current_index]
    surah_number = current_index + 1
    audio_url = config["audio_source_pattern"].format(surah_number=surah_number)
    image_url = config["image_source"].format(surah_number=surah_number)
    caption = CAPTION_TEMPLATE.format(surah_name=surah_name)

    bot = Bot(token=TOKEN)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as img_resp:
                if img_resp.status == 200:
                    image_data = await img_resp.read()
                    await bot.send_photo(chat_id=CHANNEL_ID, photo=image_data, caption=caption)
                else:
                    await bot.send_message(chat_id=CHANNEL_ID, text=caption)

            await bot.send_audio(chat_id=CHANNEL_ID, audio=audio_url)

        sent_count += 1
        current_index = (current_index + 1) % len(SURAHS)
    except Exception as e:
        print("Error sending surah:", e)

async def send_now(update, context):
    await send_surah()
    await update.message.reply_text("✅ تم إرسال السورة الآن إلى القناة.")

async def stats(update, context):
    await update.message.reply_text(f"📊 عدد السور المرسلة: {sent_count}\n📖 آخر سورة: {SURAHS[current_index-1]}\n⏱️ الوقت: {datetime.datetime.now().strftime('%H:%M:%S')}")

async def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("send_now", send_now))
    app.add_handler(CommandHandler("stats", stats))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_surah, "interval", minutes=config["send_interval_minutes"])
    scheduler.start()

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
