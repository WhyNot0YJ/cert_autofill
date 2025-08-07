from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_, and_
from datetime import datetime
import uuid
import os
from ..main import db

application_bp = Blueprint('application', __name__)

# 定义模型类
class ApplicationManagement(db.Model):
    """申请书管理模型"""
    __tablename__ = 'application_management'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    application_number = db.Column(db.String(100), unique=True, index=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    application_type = db.Column(db.String(50), nullable=False)  # 认证类型
    status = db.Column(db.String(20), default='draft')  # draft, submitted, processing, approved, rejected
    
    # 基础信息
    approval_no = db.Column(db.String(100))
    information_folder_no = db.Column(db.String(100))
    company_name = db.Column(db.String(200))
    company_address = db.Column(db.String(500))
    
    # 技术参数
    windscreen_thick = db.Column(db.String(50))
    interlayer_thick = db.Column(db.String(50))
    glass_layers = db.Column(db.String(50))
    interlayer_layers = db.Column(db.String(50))
    interlayer_type = db.Column(db.String(100))
    glass_treatment = db.Column(db.String(100))
    coating_type = db.Column(db.String(100))
    coating_thick = db.Column(db.String(50))
    coating_color = db.Column(db.String(100))
    material_nature = db.Column(db.String(100))
    safety_class = db.Column(db.String(50))
    pane_desc = db.Column(db.String(200))
    
    # 车辆信息 (JSON格式存储多个车辆)
    vehicles = db.Column(db.JSON, default=list)
    
    # 备注信息
    remarks = db.Column(db.Text)
    
    # 文件路径
    application_file_path = db.Column(db.String(500))
    report_file_path = db.Column(db.String(500))
    generated_document_path = db.Column(db.String(500))
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    
    # 关联用户 (暂时移除外键约束)
    created_by = db.Column(db.Integer, nullable=True)
    submitted_by = db.Column(db.Integer, nullable=True)
    approved_by = db.Column(db.Integer, nullable=True)
    
    # 会话ID (用于临时存储)
    session_id = db.Column(db.String(100), unique=True, index=True)
    
    def __repr__(self):
        return f"<ApplicationManagement(id={self.id}, number='{self.application_number}', status='{self.status}')>"

class ApplicationHistory(db.Model):
    """申请书历史记录模型"""
    __tablename__ = 'application_history'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application_management.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # create, update, submit, approve, reject
    description = db.Column(db.Text)
    changed_data = db.Column(db.JSON)  # 存储变更的数据
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ApplicationHistory(id={self.id}, application_id={self.application_id}, action='{self.action}')>"

class ApplicationDocument(db.Model):
    """申请书文档模型"""
    __tablename__ = 'application_documents'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application_management.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # application, report, generated
    file_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"<ApplicationDocument(id={self.id}, application_id={self.application_id}, type='{self.document_type}')>"

@application_bp.route('/applications', methods=['GET'])
def list_applications():
    """获取申请书列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        
        # 构建查询
        query = ApplicationManagement.query
        
        # 状态过滤
        if status:
            query = query.filter(ApplicationManagement.status == status)
        
        # 搜索过滤
        if search:
            search_filter = or_(
                ApplicationManagement.application_number.contains(search),
                ApplicationManagement.title.contains(search),
                ApplicationManagement.company_name.contains(search),
                ApplicationManagement.approval_no.contains(search)
            )
            query = query.filter(search_filter)
        
        # 排序和分页
        applications = query.order_by(ApplicationManagement.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 格式化返回数据
        result = {
            "success": True,
            "data": {
                "applications": [],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": applications.total,
                    "pages": applications.pages
                }
            }
        }
        
        for app in applications.items:
            result["data"]["applications"].append({
                "id": app.id,
                "application_number": app.application_number,
                "title": app.title,
                "application_type": app.application_type,
                "status": app.status,
                "company_name": app.company_name,
                "approval_no": app.approval_no,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "updated_at": app.updated_at.isoformat() if app.updated_at else None,
                "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"获取申请书列表失败: {str(e)}"}), 500 