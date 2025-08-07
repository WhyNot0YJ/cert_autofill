from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    template_type = Column(String(50), nullable=False)  # application, certificate, report
    version = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    description = Column(Text)
    variables = Column(Text)  # JSON格式存储模板变量
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', type='{self.template_type}')>" 