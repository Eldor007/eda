import psycopg2

# Настройка подключения
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="telegram_bot",
            user="postgres",
            password="Exeteruni1#",  # Ваш пароль
            host="eda.cvmmkqociyon.eu-north-1.rds.amazonaws.com",  # Ваш endpoint
            port="5432"
        )
        print("Успешно подключились к базе данных!")
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


# Пример выполнения SQL-запроса
def fetch_all_cafes():
    conn = connect_to_db()
    if conn is None:
        return  # Если подключение не удалось, завершить выполнение

    try:
        cursor = conn.cursor()
        # Выполняем запрос к таблице cafes
        cursor.execute("SELECT * FROM cafes;")
        rows = cursor.fetchall()
        
        # Выводим данные
        print("Список заведений:")
        for row in rows:
            print(row)

    except psycopg2.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
    finally:
        # Закрываем соединение
        cursor.close()
        conn.close()
        print("Соединение с базой данных закрыто.")


if __name__ == '__main__':
    fetch_all_cafes()
