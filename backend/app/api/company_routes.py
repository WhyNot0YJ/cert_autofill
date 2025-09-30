#!/usr/bin/env python3
"""
公司管理API路由
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from ..models import Company
from ..main import db
from ..utils.json_handler import JSONFieldHandler
from ..services.file_upload_service import FileUploadService

company_bp = Blueprint('company', __name__)


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
                Company.address.like(search_filter) |
                Company.country.like(search_filter)
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
        
        try:
            if 'picture' in request.files:
                file = request.files['picture']
                if file and file.filename:
                    upload_result = FileUploadService.upload_company_file(file, 'picture')
                    picture_path = upload_result['public_url']
        except ValueError as e:
            return jsonify({"error": f"图片上传失败: {str(e)}"}), 400
        
        try:
            if 'signature' in request.files:
                file = request.files['signature']
                if file and file.filename:
                    upload_result = FileUploadService.upload_company_file(file, 'signature')
                    signature_path = upload_result['public_url']
        except ValueError as e:
            return jsonify({"error": f"签名上传失败: {str(e)}"}), 400
        
        # 兼容：当前端已通过 /api/mvp/upload-file 得到 URL，直接写入
        if not picture_path and data.get('picture'):
            picture_path = data.get('picture')
        if not signature_path and data.get('signature'):
            signature_path = data.get('signature')
        
        # 处理JSON字段
        try:
            trade_names_json = JSONFieldHandler.process_trade_names(data)
            trade_marks_json = JSONFieldHandler.process_trade_marks(data)
            equipment_json = JSONFieldHandler.process_equipment(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        # 创建公司记录
            company = Company(
            name=data['name'],
            company_contraction=data.get('company_contraction', ''),
            address=data.get('address', ''),
            signature_name=data.get('signature_name', ''),
            place=data.get('place', ''),
            email_address=data.get('email_address', ''),
                country=data.get('country', ''),
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
        if 'signature_name' in data:
            company.signature_name = data['signature_name']
        if 'place' in data:
            company.place = data['place']
        if 'email_address' in data:
            company.email_address = data['email_address']
        if 'country' in data:
            company.country = data['country']
        
        # 处理JSON字段
        try:
            if 'trade_names' in data:
                company.trade_names = JSONFieldHandler.process_trade_names(data)
            if 'trade_marks' in data:
                company.trade_marks = JSONFieldHandler.process_trade_marks(data)
            if 'equipment' in data:
                company.equipment = JSONFieldHandler.process_equipment(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        if 'signature' in data:
            company.signature = data['signature']
        if 'picture' in data:
            company.picture = data['picture']
        
        # 处理图片更新
        try:
            if 'picture' in request.files:
                file = request.files['picture']
                if file and file.filename:
                    upload_result = FileUploadService.upload_company_file(file, 'picture')
                    company.picture = upload_result['public_url']
        except ValueError as e:
            return jsonify({"error": f"图片上传失败: {str(e)}"}), 400
        
        try:
            if 'signature' in request.files:
                file = request.files['signature']
                if file and file.filename:
                    upload_result = FileUploadService.upload_company_file(file, 'signature')
                    company.signature = upload_result['public_url']
        except ValueError as e:
            return jsonify({"error": f"签名上传失败: {str(e)}"}), 400
        
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
