from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from ..main import db

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(100), unique=True, index=True, nullable=False)
    approval_no = Column(String(100), index=True)  # 批准号
    enterprise_id = Column(Integer, ForeignKey('enterprises.id'), nullable=False)
    title = Column(String(200), nullable=False)
    application_type = Column(String(50), nullable=False)  # 认证类型
    status = Column(String(20), default='draft')  # draft, submitted, processing, approved, rejected
    submitted_by = Column(Integer, ForeignKey('users.id'))
    submitted_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime)
    remarks = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Application(id={self.id}, number='{self.application_number}', status='{self.status}')>"

class ApplicationVersion(db.Model):
    __tablename__ = 'application_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_data = Column(Text)  # JSON格式存储提取的数据
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ApplicationVersion(id={self.id}, application_id={self.application_id}, version={self.version_number})>" 