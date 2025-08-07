from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from ..main import db

class Enterprise(db.Model):
    __tablename__ = 'enterprises'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    english_name = Column(String(200))
    registration_number = Column(String(100), unique=True, index=True)
    legal_representative = Column(String(100))
    contact_person = Column(String(100))
    contact_phone = Column(String(50))
    contact_email = Column(String(100))
    address = Column(Text)
    business_scope = Column(Text)
    industry_type = Column(String(100))
    establishment_date = Column(DateTime)
    registered_capital = Column(String(100))
    employee_count = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Enterprise(id={self.id}, name='{self.name}')>" 