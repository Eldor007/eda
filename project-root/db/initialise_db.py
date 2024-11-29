from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

# Подключение к базе данных
DATABASE_URL = 'postgresql+psycopg2://postgres:@localhost:5432/telegram_bot'

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Модели базы данных
class Cafe(Base):
    __tablename__ = 'cafes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    district = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    type = Column(String)

    products = relationship('Product', back_populates='cafe')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    cafe_id = Column(Integer, ForeignKey('cafes.id'))
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float)

    cafe = relationship('Cafe', back_populates='products')

# Создание таблиц
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")

if __name__ == '__main__':
    create_tables()
