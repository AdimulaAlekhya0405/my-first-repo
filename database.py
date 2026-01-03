# app/database.py
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# EXAMPLE → replace with your actual MySQL credentials
DATABASE_URL = "mysql+aiomysql://root:12345@localhost:3306/pizza_delivery"

engine = create_async_engine(DATABASE_URL, echo=True)
class Base(DeclarativeBase):
    pass

AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False
)


