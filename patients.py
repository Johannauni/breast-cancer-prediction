from shared import db
from sqlalchemy import Column, Integer, String, ForeignKey

class Patient(db.Model):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    name = Column('name', String(100))
    result = Column('result', String(50))
    user_id = Column(Integer, ForeignKey('users.id')) # ← wer hat diesen Patienten angelegt