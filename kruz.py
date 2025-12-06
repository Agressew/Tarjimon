import os
import telebot
from deep_translator import GoogleTranslator
import speech_recognition as sr
from pydub import AudioSegment

TOKEN = "8545104152:AAGCxaZDfR4EpF89GJx97xJ9y2PmukPRqyw"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

user_state = {}

# ———————— BAYROQLI MENYU ————————
def main_menu():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("🇺🇿 O‘zbek → 🇰🇷 Koreys")
    kb.add("🇰🇷 Koreys → 🇺🇿 O‘zbek")
    kb.add("🇰🇷 Koreys → 🇷🇺 Русский")
    kb.add("🇷🇺 Русский → 🇰🇷 Koreys")
    return kb

def back_button(lang: str):
    text = {"uz": "Chiqish", "ru": "Назад", "ko": "뒤로"}[lang]
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(text)
    return kb

# ———————— START ————————
@bot.message_handler(commands=["start"])
def start(message):
    user_state.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "Til juftligini tanlang 🔁 \n\n""언어 쌍을 선택하세요 🔁\n\n""Выберите пару языков 🔁", reply_markup=main_menu())

# ———————— MATN + TUGMALAR ————————
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    text = message.text.strip()

    # Chiqish tugmalari
    if text in ["Chiqish", "Назад", "뒤로"]:
        user_state.pop(uid, None)
        bot.reply_to(message, "Yangi til juftligini tanlang 🔁\n\n""새 언어 쌍 선택 🔁 \n\n""Выберите новую языковую пару 🔁", reply_markup=main_menu())
        return

    # Rejim tanlash (bayroqlar bilan)
    modes = {
        "🇺🇿 O‘zbek → 🇰🇷 Koreys": ("uz", "ko", "uz"),
        "🇰🇷 Koreys → 🇺🇿 O‘zbek": ("ko", "uz", "ko"),
        "🇰🇷 Koreys → 🇷🇺 Русский": ("ko", "ru", "ko"),
        "🇷🇺 Русский → 🇰🇷 Koreys": ("ru", "ko", "ru")
    }

    if text in modes:
        src, tgt, back_lang = modes[text]
        user_state[uid] = {"src": src, "tgt": tgt}
        clean_text = text.replace("🇺🇿 ", "").replace("🇰🇷 ", "").replace("🇷🇺 ", "")
        bot.reply_to(
            message,
            f"<b>{clean_text}</b> Active.\n\n""Matn yoki ovoz yuboring 🎙\n\n""텍스트나 음성을 보내세요 🎙\n\n" "Отправьте текст или голос 🎙",
            reply_markup=back_button(back_lang)
        )
        return

    # Tarjima rejimida
    if uid not in user_state:
        bot.reply_to(message, "Avval til tanlang🤐\n\n" "먼저 언어를 선택하세요🤐\n\n" "Сначала выберите язык🤐")
        return

    src, tgt = user_state[uid]["src"], user_state[uid]["tgt"]
    try:
        result = GoogleTranslator(source=src, target=tgt).translate(text)
        bot.reply_to(message, result)  # Bayroq yo‘q
    except:
        bot.reply_to(message, "Tarjima xatosi.")

# ———————— OVOZLI XABAR ————————
@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    uid = message.from_user.id
    if uid not in user_state:
        bot.reply_to(message, "Avval til tanlang🤐\n\n" "먼저 언어를 선택하세요🤐\n\n" "Сначала выберите язык🤐")
        return

    src, tgt = user_state[uid]["src"], user_state[uid]["tgt"]

    try:
        file_info = bot.get_file(message.voice.file_id)
        voice_data = bot.download_file(file_info.file_path)

        ogg = f"v_{uid}.ogg"
        wav = f"v_{uid}.wav"

        with open(ogg, "wb") as f:
            f.write(voice_data)
        AudioSegment.from_file(ogg).export(wav, format="wav")

        r = sr.Recognizer()
        with sr.AudioFile(wav) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language=src)

        result = GoogleTranslator(source=src, target=tgt).translate(text)
        bot.reply_to(message, result)

        os.remove(ogg)
        os.remove(wav)
    except:
        bot.reply_to(message, "Ovoz xatosi.")

# ———————— ISHGA TUSHIRISH ————————
if __name__ == "__main__":
    print("Bot ishga tushdi @uzkrbot")
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print("Xato:", e)
            time.sleep(5)