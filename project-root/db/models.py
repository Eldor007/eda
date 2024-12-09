from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

# Настройка базы данных
DATABASE_URL = 'postgresql+psycopg2://postgres:Exeteruni1#@database-1.c18ec4wiiab3.ap-south-1.rds.amazonaws.com:5432/mydb'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Определение базового класса для моделей
Base = declarative_base()

class Cafe(Base):
    __tablename__ = 'cafes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    district = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    type = Column(String)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    cafe_id = Column(Integer, ForeignKey('cafes.id'))
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer, default=0) 
    cafe = relationship('Cafe', back_populates='products')

Cafe.products = relationship('Product', back_populates='cafe')
