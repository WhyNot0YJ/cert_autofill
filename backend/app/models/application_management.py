from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

# 这个文件将在main.py中被正确导入和初始化

def create_models(db):
    """创建模型类"""
    
    class ApplicationManagement(db.Model):
        """申请书管理模型"""
        __tablename__ = 'application_management'
        
        id = Column(Integer, primary_key=True, index=True)
        application_number = Column(String(100), unique=True, index=True, nullable=False)
        title = Column(String(200), nullable=False)
        application_type = Column(String(50), nullable=False)  # 认证类型
        status = Column(String(20), default='draft')  # draft, submitted, processing, approved, rejected
        
        # 基础信息
        approval_no = Column(String(100))
        information_folder_no = Column(String(100))
        company_name = Column(String(200))
        company_address = Column(String(500))
        
        # 技术参数
        windscreen_thick = Column(String(50))
        interlayer_thick = Column(String(50))
        glass_layers = Column(String(50))
        interlayer_layers = Column(String(50))
        interlayer_type = Column(String(100))
        glass_treatment = Column(String(100))
        coating_type = Column(String(100))
        coating_thick = Column(String(50))
        coating_color = Column(String(100))
        material_nature = Column(String(100))
        safety_class = Column(String(50))
        pane_desc = Column(String(200))
        
        # 车辆信息 (JSON格式存储多个车辆)
        vehicles = Column(JSON, default=list)
        
        # 备注信息
        remarks = Column(Text)
        
        # 文件路径
        application_file_path = Column(String(500))
        report_file_path = Column(String(500))
        generated_document_path = Column(String(500))
        
        # 时间戳
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        submitted_at = Column(DateTime)
        approved_at = Column(DateTime)
        
        # 关联用户
        created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
        submitted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
        approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
        
        # 会话ID (用于临时存储)
        session_id = Column(String(100), unique=True, index=True)
        
        def __repr__(self):
            return f"<ApplicationManagement(id={self.id}, number='{self.application_number}', status='{self.status}')>"

    class ApplicationHistory(db.Model):
        """申请书历史记录模型"""
        __tablename__ = 'application_history'
        
        id = Column(Integer, primary_key=True, index=True)
        application_id = Column(Integer, ForeignKey('application_management.id'), nullable=False)
        action = Column(String(50), nullable=False)  # create, update, submit, approve, reject
        description = Column(Text)
        changed_data = Column(JSON)  # 存储变更的数据
        created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f"<ApplicationHistory(id={self.id}, application_id={self.application_id}, action='{self.action}')>"

    class ApplicationDocument(db.Model):
        """申请书文档模型"""
        __tablename__ = 'application_documents'
        
        id = Column(Integer, primary_key=True, index=True)
        application_id = Column(Integer, ForeignKey('application_management.id'), nullable=False)
        document_type = Column(String(50), nullable=False)  # application, report, generated
        file_name = Column(String(200), nullable=False)
        file_path = Column(String(500), nullable=False)
        file_size = Column(Integer)
        mime_type = Column(String(100))
        uploaded_at = Column(DateTime, default=datetime.utcnow)
        uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=True)
        
        def __repr__(self):
            return f"<ApplicationDocument(id={self.id}, application_id={self.application_id}, type='{self.document_type}')>"

    return ApplicationManagement, ApplicationHistory, ApplicationDocument 