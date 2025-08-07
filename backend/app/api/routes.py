from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from ..models import Document, DocumentUpload, FormData
from ..services.extract import extract_fields
from ..services.generate import generate_document

api_bp = Blueprint('api', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== 申请书管理 ====================

@api_bp.route('/applications', methods=['GET'])
def get_applications():
    """获取申请书列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '')
        search = request.args.get('search', '')  # 搜索关键词
        
        query = FormData.query.filter(FormData.is_active == True)
        
        if status:
            query = query.filter(FormData.status == status)
        
        # 添加搜索功能
        if search:
            # 使用更安全的搜索方式，处理空值
            search_term = f"%{search}%"
            query = query.filter(
                (FormData.approval_no.isnot(None) & FormData.approval_no.like(search_term)) |
                (FormData.title.isnot(None) & FormData.title.like(search_term)) |
                (FormData.information_folder_no.isnot(None) & FormData.information_folder_no.like(search_term)) |
                (FormData.session_id.isnot(None) & FormData.session_id.like(search_term)) |
                (FormData.company_name.isnot(None) & FormData.company_name.like(search_term))
            )
        
        applications = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "success": True,
            "data": {
                "applications": [
                    {
                        "id": a.id,
                        "application_number": a.session_id,  # 使用session_id作为申请编号
                        "approval_no": a.approval_no or '',
                        "title": a.title or '',
                        "application_type": "玻璃认证",  # 默认类型
                        "status": a.status or 'draft',
                        "information_folder_no": a.information_folder_no or '',
                        "safety_class": a.safety_class or '',
                        "company_name": a.company_name or '',
                        "created_at": a.created_at.isoformat() if a.created_at else None,
                        "updated_at": a.updated_at.isoformat() if a.updated_at else None
                    } for a in applications.items
                ],
                "total": applications.total,
                "pages": applications.pages,
                "current_page": page
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"获取申请书列表失败: {str(e)}"}), 500

@api_bp.route('/applications/<int:application_id>', methods=['GET'])
def get_application(application_id):
    """获取申请书详情"""
    try:
        application = FormData.query.get_or_404(application_id)
        
        return jsonify({
            "success": True,
            "data": {
                "id": application.id,
                "application_number": application.session_id,
                "approval_no": application.approval_no,
                "title": application.title,
                "application_type": "玻璃认证",
                "status": application.status,
                "information_folder_no": application.information_folder_no,
                "safety_class": application.safety_class,
                "pane_desc": application.pane_desc,
                "glass_layers": application.glass_layers,
                "interlayer_layers": application.interlayer_layers,
                "windscreen_thick": application.windscreen_thick,
                "interlayer_thick": application.interlayer_thick,
                "glass_treatment": application.glass_treatment,
                "interlayer_type": application.interlayer_type,
                "coating_type": application.coating_type,
                "coating_thick": application.coating_thick,
                "material_nature": application.material_nature,
                "coating_color": application.coating_color,
                "remarks": application.remarks,
                "company_name": application.company_name,
                "vehicles": application.vehicles or [],
                "created_at": application.created_at.isoformat() if application.created_at else None,
                "updated_at": application.updated_at.isoformat() if application.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"获取申请书详情失败: {str(e)}"}), 500

@api_bp.route('/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    """删除申请书"""
    try:
        application = FormData.query.get_or_404(application_id)
        
        # 软删除：将is_active设置为False
        application.is_active = False
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "申请书删除成功"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"删除申请书失败: {str(e)}"}), 500

# ==================== 文件下载 ====================

@api_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载生成的文件"""
    try:
        from flask import send_from_directory, current_app
        
        # 使用与mvp_routes.py相同的路径配置
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        
        # 确保目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        # 检查文件是否存在
        file_path = os.path.join(upload_folder, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": f"文件不存在: {filename}"}), 404
        
        # 返回文件
        return send_from_directory(upload_folder, filename, as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": f"下载文件时出错: {str(e)}"}), 500

@api_bp.route('/test-download', methods=['GET'])
def test_download():
    """测试下载功能"""
    try:
        from flask import send_from_directory, current_app
        
        # 使用与mvp_routes.py相同的路径配置
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        
        # 确保目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        # 创建一个测试文件
        test_filename = "test_download.txt"
        test_file_path = os.path.join(upload_folder, test_filename)
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("这是一个测试下载功能的文件\n")
            f.write("如果你能看到这个文件，说明下载功能正常工作\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return jsonify({
            "success": True,
            "message": "测试文件已创建",
            "data": {
                "filename": test_filename,
                "download_url": f"/api/download/{test_filename}"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"创建测试文件失败: {str(e)}"}), 500

# ==================== 健康检查 ====================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy", 
        "message": "TÜV NORD 证书管理系统后端服务正常运行",
        "timestamp": datetime.now().isoformat()
    })