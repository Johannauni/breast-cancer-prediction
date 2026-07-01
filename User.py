from shared import db
from sqlalchemy import Column, Integer, String


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column('name', String(100))
    email = Column('email', String(100), unique=True)
    password = Column('password', String(200))