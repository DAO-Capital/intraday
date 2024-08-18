from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Run the postgres_setup/postgres_setup script to create the database and user
# Add _mac/_linux/_windows to the file name depending on your OS

DATABASE = "intraday_db"
USER = "postgres" # Put user name here
PASSWORD = "your_password"
HOST = "localhost"
PORT = "5432"

# Create an engine to connect to the PostgreSQL database
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base() # Base class

class Stock(Base):
    __tablename__ = 'stock'
    stock_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol = Column(String(5), nullable=False, unique=True)
    market = Column(String(50), nullable=False)

class TmpPrice(Base):
    __tablename__ = 'tmp_price'
    tmp_price_id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(String(10), nullable=False)
    date = Column(DateTime(timezone=False), nullable=False)
    px_close = Column(Numeric(15, 10), nullable=False)
    protocol = Column(String(255), nullable=False)

class Price(Base):
    __tablename__ = 'price'
    price_id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey('stock.stock_id'), nullable=False)
    price_datetime = Column(DateTime(timezone=False), nullable=False)
    stock = relationship("Stock")

def create_tables():
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
