from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from geopy.distance import geodesic
import pandas as pd

# Conversation states
LANGUAGE, LOCATION, RANGE, DISTRICT = range(4)

# Sample cafe data
cafes_data = pd.DataFrame({
    'name': ['Cafe A', 'Restaurant B', 'Cafe C'],
    'address': ['Mirzo-Ulugbek', 'Chilanzar', 'Yunusabad'],
    'type': ['Cafe', 'Restaurant', 'Cafe'],
    'location': [(41.311151, 69.279737), (41.314535, 69.282349), (41.316135, 69.285467)]
})

# District translations
districts_translations = {
    'ru': [
        'Мирзо-Улугбек', 'Чиланзар', 'Юнусабад', 'Яшнабад',
        'Шайхантахур', 'Алмазар', 'Сергелийский', 'Уртачирчик',
        'Бектемир', 'Мирабад', 'Яккасарай', 'Собир Рахимов'
    ],
    'en': [
        'Mirzo-Ulugbek', 'Chilanzar', 'Yunusabad', 'Yashnabad',
        'Shaykhantohur', 'Almazar', 'Sergeli', 'Urtachirchik',
        'Bektemir', 'Mirabad', 'Yakkasaray', 'Sobir Rahimov'
    ],
    'uz': [
        'Mirzo Ulug‘bek', 'Chilonzor', 'Yunusobod', 'Yashnobod',
        'Shayxontohur', 'Olmazor', 'Sergeli', 'O‘rta Chirchiq',
        'Bektemir', 'Mirabad', 'Yakkasaroy', 'Sobir Rahimov'
    ]
}

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
    'choose_range': {
        'ru': "Выберите диапазон поиска",
        'en': "Select the search range",
        'uz': "Qidiruv masofasini tanlang"
    },
    'no_offers': {
        'ru': "Поблизости нет кафе с предложениями.",
        'en': "There are no cafes nearby with offers.",
        'uz': "Atrofingizda takliflar bilan kafelar yo'q."
    },
    'back': {
        'ru': "🔙 Назад",
        'en': "🔙 Back",
        'uz': "🔙 Ortga"
    },
    'range_options': {
        'ru': ['1 км', '2 км', '5 км'],
        'en': ['1 km', '2 km', '5 km'],
        'uz': ['1 km', '2 km', '5 km']
    }
}

# Map states to handler functions
state_handlers = {}

# Start command
async def start_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_buttons = [
        [KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇺🇸 English"), KeyboardButton("🇺🇿 O‘zbek")]
    ]
    await update.message.reply_text(
        "Выберите язык / Select your language / Tilni tanlang",
        reply_markup=ReplyKeyboardMarkup(language_buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    context.user_data.clear()  # Сбрасываем состояние
    context.user_data['state_stack'] = []
    return LANGUAGE

# Push current state to the stack
def push_state(context, state):
    if 'state_stack' not in context.user_data:
        context.user_data['state_stack'] = []
    context.user_data['state_stack'].append(state)

# Pop the last state from the stack
def pop_state(context):
    if 'state_stack' in context.user_data and context.user_data['state_stack']:
        return context.user_data['state_stack'].pop()
    return None

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
            [translations['choose_district'][language]],
            [translations['back'][language]]
        ]
        await update.message.reply_text(
            translations['location_or_district'][language],
            reply_markup=ReplyKeyboardMarkup(location_buttons, one_time_keyboard=True, resize_keyboard=True)
        )
        # Добавляем LANGUAGE в стек **перед** переходом на новое состояние
        push_state(context, LANGUAGE)
        return LOCATION
    else:
        # Повторяем выбор языка
        return await start_info(update, context)

# Handle location or district selection
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')

    if update.message.location:
        user_location = (update.message.location.latitude, update.message.location.longitude)
        context.user_data['location'] = user_location
        range_buttons = translations['range_options'][language] + [translations['back'][language]]
        await update.message.reply_text(
            translations['choose_range'][language],
            reply_markup=ReplyKeyboardMarkup([range_buttons], one_time_keyboard=True, resize_keyboard=True)
        )
        # Добавляем LOCATION в стек **перед** переходом на новое состояние
        push_state(context, LOCATION)
        return RANGE

    elif update.message.text == translations['choose_district'][language]:
        district_buttons = [
            [district] for district in districts_translations[language]
        ]
        district_buttons.append([translations['back'][language]])
        await update.message.reply_text(
            translations['choose_district'][language],
            reply_markup=ReplyKeyboardMarkup(district_buttons, one_time_keyboard=True, resize_keyboard=True)
        )
        # Добавляем LOCATION в стек **перед** переходом на новое состояние
        push_state(context, LOCATION)
        return DISTRICT

    elif update.message.text == translations['back'][language]:
        previous_state = pop_state(context)
        if previous_state is not None:
            # Возвращаемся к предыдущему состоянию
            handler = state_handlers.get(previous_state, start_info)
            return await handler(update, context)
        else:
            # Если стек пуст, возвращаемся к старту
            return await start_info(update, context)

    else:
        # Повторяем запрос отправки локации или выбора района
        location_buttons = [
            [KeyboardButton(translations['send_location'][language], request_location=True)],
            [translations['choose_district'][language]],
            [translations['back'][language]]
        ]
        await update.message.reply_text(
            translations['location_or_district'][language],
            reply_markup=ReplyKeyboardMarkup(location_buttons, one_time_keyboard=True, resize_keyboard=True)
        )
        return LOCATION

# Handle range selection
async def handle_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')
    selected_range = update.message.text

    if selected_range == translations['back'][language]:
        previous_state = pop_state(context)
        if previous_state is not None:
            handler = state_handlers.get(previous_state, start_info)
            return await handler(update, context)
        else:
            return await start_info(update, context)

    try:
        range_km = int(selected_range.split()[0])
        user_location = context.user_data.get('location')
        if user_location:
            nearby_cafes = [
                f"{cafe['name']} - {cafe['type']} ({round(geodesic(user_location, cafe['location']).kilometers, 2)} km)"
                for _, cafe in cafes_data.iterrows()
                if geodesic(user_location, cafe['location']).kilometers <= range_km
            ]
            if nearby_cafes:
                await update.message.reply_text(
                    "\n".join(nearby_cafes),
                    reply_markup=ReplyKeyboardMarkup([[translations['back'][language]]], one_time_keyboard=True, resize_keyboard=True)
                )
            else:
                await update.message.reply_text(
                    translations['no_offers'][language],
                    reply_markup=ReplyKeyboardMarkup([[translations['back'][language]]], one_time_keyboard=True, resize_keyboard=True)
                )
            # Добавляем RANGE в стек
            push_state(context, RANGE)
            return RANGE
        else:
            # Если по какой-то причине нет локации пользователя
            return await handle_location(update, context)
    except ValueError:
        # Если пользователь ввел некорректный диапазон
        range_buttons = translations['range_options'][language] + [translations['back'][language]]
        await update.message.reply_text(
            translations['choose_range'][language],
            reply_markup=ReplyKeyboardMarkup([range_buttons], one_time_keyboard=True, resize_keyboard=True)
        )
        return RANGE

# Handle district selection
async def handle_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')
    selected_district = update.message.text

    if selected_district == translations['back'][language]:
        previous_state = pop_state(context)
        if previous_state is not None:
            handler = state_handlers.get(previous_state, start_info)
            return await handler(update, context)
        else:
            return await start_info(update, context)

    elif selected_district in districts_translations[language]:
        cafes_in_district = cafes_data[cafes_data['address'] == selected_district]
        cafes_list = [f"{row['name']} - {row['type']}" for _, row in cafes_in_district.iterrows()]
        if cafes_list:
            await update.message.reply_text(
                "\n".join(cafes_list),
                reply_markup=ReplyKeyboardMarkup([[translations['back'][language]]], one_time_keyboard=True, resize_keyboard=True)
            )
        else:
            await update.message.reply_text(
                translations['no_offers'][language],
                reply_markup=ReplyKeyboardMarkup([[translations['back'][language]]], one_time_keyboard=True, resize_keyboard=True)
            )
        # Добавляем DISTRICT в стек
        push_state(context, DISTRICT)
        return DISTRICT

    else:
        # Если введен некорректный район
        district_buttons = [
            [district] for district in districts_translations[language]
        ]
        district_buttons.append([translations['back'][language]])
        await update.message.reply_text(
            translations['choose_district'][language],
            reply_markup=ReplyKeyboardMarkup(district_buttons, one_time_keyboard=True, resize_keyboard=True)
        )
        return DISTRICT

# Map states to handler functions
state_handlers = {
    LANGUAGE: handle_language,
    LOCATION: handle_location,
    RANGE: handle_range,
    DISTRICT: handle_district
}

# Main function
def main():
    application = Application.builder().token('7803661490:AAFM172alG5KXsW4P_H65IaUO6yIt3igsXI').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_info)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language)],
            LOCATION: [MessageHandler(filters.LOCATION | (filters.TEXT & ~filters.COMMAND), handle_location)],
            RANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_range)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_district)],
        },
        fallbacks=[CommandHandler('start', start_info)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()