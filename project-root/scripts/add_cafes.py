from models import SessionLocal, Cafe
import uuid


def generate_password_from_longitude(longitude):
    # Генерируем пароль на основе последних 5-6 цифр долготы
    return str(abs(longitude)).split('.')[-1][:6]


def add_cafes():
    session = SessionLocal()
    
    # Список кафе для добавления
    cafes = [
        Cafe(
            name='Cafe A',
            address='Main St, 123',
            district='Мирзо-Улугбек',
            latitude=41.311151,
            longitude=69.279737,
            type='Кафе',
        ),
        Cafe(
            name='Restaurant B',
            address='Elm St, 45',
            district='Чиланзар',
            latitude=41.314535,
            longitude=69.282349,
            type='Ресторан',
        ),
        Cafe(
            name='Cafe C',
            address='Oak Ave, 10',
            district='Юнусабад',
            latitude=41.316135,
            longitude=69.285467,
            type='Кафе',
        )
    ]

    for cafe in cafes:
        # Устанавливаем логин как уникальный UUID (первые 8 символов)
        cafe.username = str(uuid.uuid4())[:8]

        # Генерируем пароль на основе долготы
        password = generate_password_from_longitude(cafe.longitude)
        cafe.set_password(password)

        print(f"Добавлено заведение: {cafe.name}, Логин: {cafe.username}, Пароль: {password}")

        # Добавляем запись в сессию
        session.add(cafe)

    # Сохраняем изменения в базе данных
    session.commit()
    session.close()
    print("Заведения успешно добавлены.")


if __name__ == '__main__':
    add_cafes()