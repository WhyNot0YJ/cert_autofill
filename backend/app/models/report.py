from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Report(Base):
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(100), unique=True, index=True, nullable=False)
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=False)
    certificate_id = Column(Integer, ForeignKey('certificates.id'))
    title = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # test_report, audit_report, etc.
    status = Column(String(20), default='draft')  # draft, completed, approved
    test_date = Column(DateTime)
    completed_by = Column(Integer, ForeignKey('users.id'))
    completed_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime)
    test_results = Column(Text)  # JSON格式存储测试结果
    conclusions = Column(Text)
    remarks = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Report(id={self.id}, number='{self.report_number}', type='{self.report_type}')>"

class ReportVersion(Base):
    __tablename__ = 'report_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey('reports.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    change_reason = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ReportVersion(id={self.id}, report_id={self.report_id}, version={self.version_number})>" 