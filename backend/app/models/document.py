from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from .base import Base

class Document(Base):
    """文档基础信息表"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    document_type = Column(String(50), nullable=False)  # application, report
    status = Column(String(20), default='uploaded')  # uploaded, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', type='{self.document_type}')>"

class DocumentUpload(Base):
    """文档上传记录表"""
    __tablename__ = 'document_uploads'
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))  # pdf, docx, doc
    upload_status = Column(String(20), default='uploaded')  # uploaded, processing, completed, failed
    ai_extraction_result = Column(JSON)  # AI提取的原始结果
    extracted_data = Column(JSON)  # 处理后的结构化数据
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DocumentUpload(id={self.id}, filename='{self.original_filename}')>" 