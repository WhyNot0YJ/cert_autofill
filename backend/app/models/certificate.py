from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Certificate(Base):
    __tablename__ = 'certificates'
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_number = Column(String(100), unique=True, index=True, nullable=False)
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=False)
    enterprise_id = Column(Integer, ForeignKey('enterprises.id'), nullable=False)
    title = Column(String(200), nullable=False)
    certificate_type = Column(String(50), nullable=False)
    status = Column(String(20), default='active')  # active, expired, revoked, suspended
    issue_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    issued_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    scope = Column(Text)  # 认证范围
    conditions = Column(Text)  # 认证条件
    remarks = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, number='{self.certificate_number}', status='{self.status}')>"

class CertificateVersion(Base):
    __tablename__ = 'certificate_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(Integer, ForeignKey('certificates.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    change_reason = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CertificateVersion(id={self.id}, certificate_id={self.certificate_id}, version={self.version_number})>" 