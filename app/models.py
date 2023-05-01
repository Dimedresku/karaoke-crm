import enum

from sqlalchemy import TIMESTAMP, Column, String, Boolean, Integer, Enum
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "auth_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=266), nullable=True)
    username = Column(String(length=255), nullable=False)
    password = Column(String(length=1024), nullable=False)
    avatar = Column(String(length=1024), nullable=True)
    createdAt = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, server_default=func.now())


class Events(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=255), nullable=False)
    description = Column(String(length=1024), nullable=True)
    published = Column(Boolean, nullable=False, server_default="True")
    createdAt = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, server_default=func.now())
    image = Column(String(length=1024), nullable=True)


class Reservations(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_reservation = Column(TIMESTAMP(timezone=True), nullable=False)
    people_count = Column(Integer, nullable=False)
    phone_number = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=True)
    comment = Column(String(length=1024), nullable=True)
    admin_comment = Column(String(length=1024), nullable=True)
    served = Column(Boolean, nullable=False, server_default="False")
    createdAt = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, server_default=func.now())


class MenuCategory(enum.Enum):
    ALCOHOL_DRINKS = 'alcohol_drinks'
    NON_ALCOHOL_DRINKS = 'non_alcohol_drinks'
    SNACKS = 'snacks'
    PIZZA = 'pizza'
    SUSHI = 'sushi'


class MenuItem(Base):
    __tablename__ = "menu_item"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Enum(MenuCategory, values_callable=lambda obj: [e.value for e in obj]))
    sub_category = Column(String(length=1024))
    name = Column(String(length=1024))
    sub_name = Column(String(length=1024), nullable=True)
    main_unit = Column(String(length=255))
    main_price = Column(String(length=255))
    secondary_unit = Column(String(length=255), nullable=True)
    secondary_price = Column(String(length=255), nullable=True)
    special = Column(Boolean, nullable=False, server_default="False")
    createdAt = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, server_default=func.now())
