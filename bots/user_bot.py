import sys
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from geopy.distance import geodesic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Cafe  # Ваша модель для кафе

# Добавляем путь к корневой директории проекта (если необходимо)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Подключение к базе данных через SQLAlchemy
DATABASE_URL = "postgresql+psycopg2://postgres:Exeteruni1#@eda.cvmmkqociyon.eu-north-1.rds.amazonaws.com:5432/telegram_bot"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Conversation states
LANGUAGE, LOCATION = range(2)

# Translations dictionary
translations = {
    'select_language': {
        'ru': "Выберите язык",
        'en': "Select your language",
        'uz': "Tilni tanlang"
    },
    'location_or_district': {
        'ru': "Отправьте свою локацию или выберите район",
        'en': "Send your location or choose a district",
        'uz': "Joylashuvingizni yuboring yoki tuman tanlang"
    },
    'send_location': {
        'ru': "Отправить локацию",
        'en': "Send location",
        'uz': "Joylashuvingizni yuboring"
    },
    'choose_district': {
        'ru': "Выбрать район",
        'en': "Choose district",
        'uz': "Tumanni tanlash"
    },
    'no_offers': {
        'ru': "Поблизости нет кафе с предложениями.",
        'en': "There are no cafes nearby with offers.",
        'uz': "Atrofingizda takliflar bilan kafelar yo'q."
    },
    'invalid_choice': {
        'ru': "Пожалуйста, выберите один из предложенных вариантов.",
        'en': "Please choose one of the provided options.",
        'uz': "Iltimos, taklif qilingan variantlardan birini tanlang."
    },
}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_buttons = [
        [KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇺🇸 English"), KeyboardButton("🇺🇿 O‘zbek")]
    ]
    await update.message.reply_text(
        translations['select_language']['ru'],
        reply_markup=ReplyKeyboardMarkup(language_buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    context.user_data['state_stack'] = []
    return LANGUAGE

# Handle language selection
async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_language = update.message.text
    languages = {
        "🇷🇺 Русский": 'ru',
        "🇺🇸 English": 'en',
        "🇺🇿 O‘zbek": 'uz'
    }

    if selected_language in languages:
        context.user_data['language'] = languages[selected_language]
        language = context.user_data['language']

        location_buttons = [
            [KeyboardButton(translations['send_location'][language], request_location=True)],
            [KeyboardButton(translations['choose_district'][language])]
        ]
        await update.message.reply_text(
            translations['location_or_district'][language],
            reply_markup=ReplyKeyboardMarkup(location_buttons, one_time_keyboard=True, resize_keyboard=True)
        )
        return LOCATION
    else:
        await update.message.reply_text(translations['invalid_choice']['ru'])
        return LANGUAGE

# Handle location or district selection
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')

    if update.message.location:
        user_location = (update.message.location.latitude, update.message.location.longitude)
        session = SessionLocal()
        nearby_cafes = session.query(Cafe).all()  # Пример запроса к базе
        cafes_in_range = [
            f"{cafe.name} ({geodesic(user_location, (cafe.latitude, cafe.longitude)).km:.2f} km)"
            for cafe in nearby_cafes
            if geodesic(user_location, (cafe.latitude, cafe.longitude)).km <= 5
        ]
        session.close()

        if cafes_in_range:
            await update.message.reply_text("\n".join(cafes_in_range))
        else:
            await update.message.reply_text(translations['no_offers'][language])
        return LOCATION
    elif update.message.text == translations['choose_district'][language]:
        await update.message.reply_text("Функционал выбора района пока не реализован.")
        return LOCATION
    else:
        await update.message.reply_text(translations['invalid_choice'][language])
        return LOCATION

# Main function
def main():
    application = (
        ApplicationBuilder()
        .token("7803661490:AAFwVl_ZFAhDCzO1r0DvprT82pcVHV7ab8Q")  # Убедитесь, что токен верный
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language)],
            LOCATION: [MessageHandler(filters.LOCATION | (filters.TEXT & ~filters.COMMAND), handle_location)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)

    # Запуск polling
    application.run_polling()

if __name__ == "__main__":
    main()
