from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from db.models import SessionLocal, Cafe, Product  # Убедитесь, что модель Product определена
from prettytable import PrettyTable  # Для отображения таблицы

AUTHENTICATE, ADD_PRODUCT, EDIT_PRODUCT = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать! Пожалуйста, введите ваш логин (ID заведения):"
    )
    return AUTHENTICATE


async def authenticate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    session = SessionLocal()
    cafe = session.query(Cafe).filter(Cafe.username == username).first()
    session.close()

    if cafe:
        context.user_data['cafe_id'] = cafe.id
        context.user_data['cafe_name'] = cafe.name
        await update.message.reply_text("Введите ваш пароль:")
        return AUTHENTICATE + 1
    else:
        await update.message.reply_text("Неверный логин. Попробуйте снова.")
        return AUTHENTICATE


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    session = SessionLocal()
    cafe = session.query(Cafe).filter(Cafe.id == context.user_data['cafe_id']).first()
    session.close()

    if cafe and cafe.check_password(password):
        await show_product_table(update, context)  # Показать таблицу продуктов
        return EDIT_PRODUCT
    else:
        await update.message.reply_text("Неверный пароль. Попробуйте снова.")
        return AUTHENTICATE


async def show_product_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение таблицы продуктов для заведения"""
    session = SessionLocal()
    cafe_id = context.user_data['cafe_id']
    products = session.query(Product).filter(Product.cafe_id == cafe_id).all()
    session.close()

    if products:
        table = PrettyTable()
        table.field_names = ["ID", "Название", "Описание", "Цена", "Количество"]
        for product in products:
            table.add_row([product.id, product.name, product.description, product.price, product.quantity])
        await update.message.reply_text(
            f"Вы вошли как продавец заведения {context.user_data['cafe_name']}.\n"
            f"Текущие продукты:\n\n"
            f"<pre>{table}</pre>",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(
                [['Добавить продукт', 'Редактировать продукт']], one_time_keyboard=True, resize_keyboard=True
            )
        )
    else:
        await update.message.reply_text(
            f"Вы вошли как продавец заведения {context.user_data['cafe_name']}.\n"
            "У вас пока нет добавленных продуктов.",
            reply_markup=ReplyKeyboardMarkup(
                [['Добавить продукт']], one_time_keyboard=True, resize_keyboard=True
            )
        )


async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите название продукта:")
    context.user_data['edit_action'] = 'add'
    return EDIT_PRODUCT


async def edit_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите ID продукта, который вы хотите редактировать (или нажмите 'Отмена' для выхода):"
    )
    context.user_data['edit_action'] = 'edit'
    return EDIT_PRODUCT


async def process_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка редактирования продукта"""
    action = context.user_data.get('edit_action')
    session = SessionLocal()

    if action == 'add':
        name = update.message.text.strip()
        if not name:
            await update.message.reply_text("Название продукта не может быть пустым. Попробуйте снова.")
            return EDIT_PRODUCT

        product = Product(
            name=name,
            description="Описание по умолчанию",
            price=0.0,
            quantity=0,
            cafe_id=context.user_data['cafe_id']
        )
        session.add(product)
        session.commit()
        session.close()

        await update.message.reply_text(f"Продукт '{name}' успешно добавлен!")
    elif action == 'edit':
        try:
            product_id = int(update.message.text.strip())
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                context.user_data['edit_product_id'] = product_id
                await update.message.reply_text(
                    "Введите новое описание для продукта:"
                )
                return EDIT_PRODUCT + 1
            else:
                await update.message.reply_text("Продукт с таким ID не найден. Попробуйте снова.")
        except ValueError:
            await update.message.reply_text("Неверный ввод. Укажите числовой ID.")
    session.close()
    return EDIT_PRODUCT


async def update_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновление описания продукта"""
    new_description = update.message.text.strip()
    session = SessionLocal()
    product_id = context.user_data.get('edit_product_id')
    product = session.query(Product).filter(Product.id == product_id).first()

    if product:
        product.description = new_description
        session.commit()
        await update.message.reply_text(f"Описание продукта '{product.name}' обновлено на: {new_description}")
    else:
        await update.message.reply_text("Ошибка обновления. Попробуйте снова.")
    session.close()
    return EDIT_PRODUCT


def main():
    application = Application.builder().token('7938013591:AAEDYM-vE5yA-WDujbs3bZqnD76DmOTwtXI').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AUTHENTICATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, authenticate)],
            AUTHENTICATE + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
            ADD_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product)],
            EDIT_PRODUCT: [
                MessageHandler(filters.Regex('^Добавить продукт$'), add_product),
                MessageHandler(filters.Regex('^Редактировать продукт$'), edit_product),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_edit),
            ],
            EDIT_PRODUCT + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_product)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
