from sqlalchemy import BigInteger, Boolean, Column, Integer, String, DateTime, Float, text
from database import Base
import sqlalchemy.sql as func

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    capital = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True, index=True)
    population = Column(BigInteger, nullable=False)
    currency_code = Column(String(10), index=True)
    exchange_rate = Column(Float)
    estimated_gdp = Column(Float, nullable=True)
    flag_url = Column(String(500), nullable=True)
    last_refreshed_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))