#!/usr/bin/env python3
"""
公司管理API路由
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from ..models import Company
from ..main import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

company_bp = Blueprint('company', __name__)

# 允许的图片文件扩展名
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@company_bp.route('/companies', methods=['GET'])
def get_companies():
    """获取公司列表 - 支持分页和搜索"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        sort_by = request.args.get('sort_by', 'created_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)
        
        # 限制每页数量
        per_page = min(per_page, 100)
        
        # 构建查询
        query = Company.query
        
        # 搜索功能
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                Company.name.like(search_filter) | 
                Company.company_contraction.like(search_filter) |
                Company.address.like(search_filter)
            )
        
        # 排序
        if hasattr(Company, sort_by):
            order_column = getattr(Company, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            # 默认按创建时间降序
            query = query.order_by(Company.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        companies = pagination.items
        
        return jsonify({
            "success": True,
            "data": {
                "companies": [company.to_dict() for company in companies],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_prev": pagination.has_prev,
                    "has_next": pagination.has_next,
                    "prev_num": pagination.prev_num,
                    "next_num": pagination.next_num
                },
                "search": search,
                "sort": {
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"获取公司列表失败: {str(e)}"}), 500


@company_bp.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """获取单个公司信息"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({"error": "公司不存在"}), 404
        
        return jsonify({
            "success": True,
            "data": company.to_dict()
        })
    except Exception as e:
        return jsonify({"error": f"获取公司信息失败: {str(e)}"}), 500


@company_bp.route('/companies', methods=['POST'])
def create_company():
    """创建新公司"""
    try:
        data = request.get_json(silent=True) or {}
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({"error": "公司名称不能为空"}), 400
        
        # 检查公司名称是否已存在
        existing_company = Company.query.filter_by(name=data['name']).first()
        if existing_company:
            return jsonify({"error": "公司名称已存在"}), 400
        
        # 处理图片上传
        picture_path = None
        signature_path = None
        
        if 'picture' in request.files:
            file = request.files['picture']
            if file and allowed_image_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"company_picture_{timestamp}_{filename}"
                
                # 确保上传目录存在
                upload_dir = os.path.join(os.getcwd(), 'uploads', 'companies')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                picture_path = f"/uploads/companies/{filename}"
        
        if 'signature' in request.files:
            file = request.files['signature']
            if file and allowed_image_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"company_signature_{timestamp}_{filename}"
                
                # 确保上传目录存在
                upload_dir = os.path.join(os.getcwd(), 'uploads', 'companies')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                signature_path = f"/uploads/companies/{filename}"
        
        # 兼容：当前端已通过 /api/mvp/upload-file 得到 URL，直接写入
        if not picture_path and data.get('picture'):
            picture_path = data.get('picture')
        if not signature_path and data.get('signature'):
            signature_path = data.get('signature')
        
        # 处理trade_names字段
        trade_names_json = None
        if 'trade_names' in data:
            import json
            try:
                # 如果传入的是数组，转换为JSON字符串
                if isinstance(data['trade_names'], list):
                    trade_names_json = json.dumps(data['trade_names'])
                elif isinstance(data['trade_names'], str):
                    # 验证是否为有效的JSON数组
                    trade_names_list = json.loads(data['trade_names'])
                    if isinstance(trade_names_list, list):
                        trade_names_json = data['trade_names']
                    else:
                        return jsonify({"error": "trade_names字段必须是字符串数组"}), 400
                elif data['trade_names'] is None:
                    trade_names_json = None
                else:
                    return jsonify({"error": "trade_names字段必须是字符串数组"}), 400
            except json.JSONDecodeError:
                return jsonify({"error": "trade_names字段格式错误，必须是有效的JSON数组"}), 400
        
        # 处理trade_marks字段
        trade_marks_json = None
        if 'trade_marks' in data:
            import json
            try:
                # 如果传入的是数组，转换为JSON字符串
                if isinstance(data['trade_marks'], list):
                    trade_marks_json = json.dumps(data['trade_marks'])
                elif isinstance(data['trade_marks'], str):
                    # 验证是否为有效的JSON数组
                    trade_marks_list = json.loads(data['trade_marks'])
                    if isinstance(trade_marks_list, list):
                        trade_marks_json = data['trade_marks']
                    else:
                        return jsonify({"error": "trade_marks字段必须是URL数组"}), 400
                elif data['trade_marks'] is None:
                    trade_marks_json = None
                else:
                    return jsonify({"error": "trade_marks字段必须是URL数组"}), 400
            except json.JSONDecodeError:
                return jsonify({"error": "trade_marks字段格式错误，必须是有效的JSON数组"}), 400
        
        # 处理equipment字段
        equipment_json = None
        if 'equipment' in data:
            import json
            try:
                # 如果传入的是数组，转换为JSON字符串
                if isinstance(data['equipment'], list):
                    # 验证设备数据格式
                    for item in data['equipment']:
                        if not isinstance(item, dict) or 'no' not in item or 'name' not in item:
                            return jsonify({"error": "设备信息格式错误，每个设备必须包含no(编号)和name(名称)字段"}), 400
                    equipment_json = json.dumps(data['equipment'])
                elif isinstance(data['equipment'], str):
                    # 验证是否为有效的JSON数组
                    equipment_list = json.loads(data['equipment'])
                    if isinstance(equipment_list, list):
                        # 验证设备数据格式
                        for item in equipment_list:
                            if not isinstance(item, dict) or 'no' not in item or 'name' not in item:
                                return jsonify({"error": "设备信息格式错误，每个设备必须包含no(编号)和name(名称)字段"}), 400
                        equipment_json = data['equipment']
                    else:
                        return jsonify({"error": "equipment字段必须是设备对象数组"}), 400
                elif data['equipment'] is None:
                    equipment_json = None
                else:
                    return jsonify({"error": "equipment字段必须是设备对象数组"}), 400
            except json.JSONDecodeError:
                return jsonify({"error": "equipment字段格式错误，必须是有效的JSON数组"}), 400
        
        # 创建公司记录
        company = Company(
            name=data['name'],
            company_contraction=data.get('company_contraction', ''),
            address=data.get('address', ''),
            trade_names=trade_names_json,
            trade_marks=trade_marks_json,
            equipment=equipment_json,
            signature=signature_path,
            picture=picture_path
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "公司创建成功",
            "data": company.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"创建公司失败: {str(e)}"}), 500


@company_bp.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    """更新公司信息"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({"error": "公司不存在"}), 404
        
        data = request.get_json(silent=True) or {}
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否与其他公司重复
            existing_company = Company.query.filter_by(name=data['name']).first()
            if existing_company and existing_company.id != company_id:
                return jsonify({"error": "公司名称已存在"}), 400
            company.name = data['name']
        
        if 'company_contraction' in data:
            company.company_contraction = data['company_contraction']
        
        if 'address' in data:
            company.address = data['address']
        
        if 'trade_names' in data:
            import json
            try:
                # 处理trade_names字段
                if data['trade_names'] is None or data['trade_names'] == '':
                    company.trade_names = None
                elif isinstance(data['trade_names'], list):
                    company.trade_names = json.dumps(data['trade_names'])
                elif isinstance(data['trade_names'], str):
                    # 验证是否为有效的JSON数组
                    trade_names_list = json.loads(data['trade_names'])
                    if isinstance(trade_names_list, list):
                        company.trade_names = data['trade_names']
                    else:
                        return jsonify({"error": "trade_names字段必须是字符串数组"}), 400
            except json.JSONDecodeError:
                return jsonify({"error": "trade_names字段格式错误，必须是有效的JSON数组"}), 400
        
        if 'trade_marks' in data:
            import json
            try:
                # 处理trade_marks字段
                if data['trade_marks'] is None or data['trade_marks'] == '':
                    company.trade_marks = None
                elif isinstance(data['trade_marks'], list):
                    company.trade_marks = json.dumps(data['trade_marks'])
                elif isinstance(data['trade_marks'], str):
                    # 验证是否为有效的JSON数组
                    trade_marks_list = json.loads(data['trade_marks'])
                    if isinstance(trade_marks_list, list):
                        company.trade_marks = data['trade_marks']
                    else:
                        return jsonify({"error": "trade_marks字段必须是URL数组"}), 400
            except json.JSONDecodeError:
                return jsonify({"error": "trade_marks字段格式错误，必须是有效的JSON数组"}), 400
        
        if 'equipment' in data:
            import json
            try:
                # 处理equipment字段
                if data['equipment'] is None or data['equipment'] == '':
                    company.equipment = None
                elif isinstance(data['equipment'], list):
                    # 验证设备数据格式
                    for item in data['equipment']:
                        if not isinstance(item, dict) or 'no' not in item or 'name' not in item:
                            return jsonify({"error": "设备信息格式错误，每个设备必须包含no(编号)和name(名称)字段"}), 400
                    company.equipment = json.dumps(data['equipment'])
                elif isinstance(data['equipment'], str):
                    # 验证是否为有效的JSON数组
                    equipment_list = json.loads(data['equipment'])
                    if isinstance(equipment_list, list):
                        # 验证设备数据格式
                        for item in equipment_list:
                            if not isinstance(item, dict) or 'no' not in item or 'name' not in item:
                                return jsonify({"error": "设备信息格式错误，每个设备必须包含no(编号)和name(名称)字段"}), 400
                        company.equipment = data['equipment']
                    else:
                        return jsonify({"error": "equipment字段必须是设备对象数组"}), 400
            except json.JSONDecodeError:
                return jsonify({"error": "equipment字段格式错误，必须是有效的JSON数组"}), 400
        
        if 'signature' in data:
            company.signature = data['signature']
        if 'picture' in data:
            company.picture = data['picture']
        
        # 处理图片更新
        if 'picture' in request.files:
            file = request.files['picture']
            if file and allowed_image_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"company_picture_{timestamp}_{filename}"
                
                # 确保上传目录存在
                upload_dir = os.path.join(os.getcwd(), 'uploads', 'companies')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                company.picture = f"/uploads/companies/{filename}"
        
        if 'signature' in request.files:
            file = request.files['signature']
            if file and allowed_image_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"company_signature_{timestamp}_{filename}"
                
                # 确保上传目录存在
                upload_dir = os.path.join(os.getcwd(), 'uploads', 'companies')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                company.signature = f"/uploads/companies/{filename}"
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "公司信息更新成功",
            "data": company.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"更新公司信息失败: {str(e)}"}), 500


@company_bp.route('/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    """删除公司"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({"error": "公司不存在"}), 404
        
        # 检查是否有关联的表单数据
        if company.form_data:
            return jsonify({"error": "该公司有关联的表单数据，无法删除"}), 400
        
        db.session.delete(company)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "公司删除成功"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"删除公司失败: {str(e)}"}), 500
