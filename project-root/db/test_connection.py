from sqlalchemy import create_engine

# Ваша строка подключения
DATABASE_URL = 'postgresql+psycopg2://postgres:Exeteruni1#@database-1.c18ec4wiiab3.ap-south-1.rds.amazonaws.com:5432/mydb'

def test_connection():
    try:
        # Создаём подключение
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        print("Успешно подключились к базе данных!")
        connection.close()
    except Exception as e:
        print("Ошибка подключения к базе данных:")
        print(e)

if __name__ == '__main__':
    test_connection()
