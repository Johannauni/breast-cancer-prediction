from shared import db
from sqlalchemy import Column, Integer, String


class Patient(db.Model):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    name = Column('name', String(100))
    email = Column('email', String(100), unique=True)
    password = Column('password', String(200))
    result = Column('result', String(50))
    user_id = Column(Integer) # ← wer hat diesen Patienten angelegt