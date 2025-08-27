from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime, date
from ..models import Document, DocumentUpload, FormData
from ..services.ai_extract import ai_extraction_service

from ..services.generators import (
    generate_if_document, generate_if_pdf_from_docx,
    generate_cert_document, create_cert_sample_data,
    generate_rcs_document, create_rcs_sample_data,
    generate_other_document, create_other_sample_data,
    generate_tr_document, create_tr_sample_data,
    generate_tm_document, create_tm_sample_data,
    generate_pm_document, create_pm_sample_data
)
from ..services.generators.rcs_generator import RcsGenerator
from ..services.generators.other_generator import OtherGenerator
from ..services.generators.tr_generator import TrGenerator
from ..services.generators.tm_generator import TmGenerator
from ..services.generators.pm_generator import PmGenerator
from ..main import db
from sqlalchemy.orm import sessionmaker
from ..models.base import Base
from ..services.ai_extract import ai_extraction_service
mvp_bp = Blueprint('mvp', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _make_safe_approval_no(form_data_obj, fallback: str = "TEST") -> str:
    """Return a filesystem-safe approval_no string for filenames."""
    import re
    if form_data_obj and getattr(form_data_obj, 'approval_no', None):
        approval_no = form_data_obj.approval_no or fallback
    else:
        approval_no = fallback
    safe = re.sub(r'[^a-zA-Z0-9]', '-', approval_no)
    safe = re.sub(r'-+', '-', safe).strip('-')
    return safe or fallback

# 在文件开头添加新的辅助函数
class DocumentGeneratorFactory:
    """文档生成器工厂类"""
    
    def __init__(self):
        self.generators = {
            'if': {
                'type': 'if',
                'name': 'IF',
                'generator': generate_if_document,
                'template': "IF_Template",
                'use_class': False,
                'special_handler': self._handle_if_document
            },
            'cert': {
                'type': 'cert',
                'name': 'CERT',
                'generator': generate_cert_document,
                'template': None,
                'use_class': False
            },
            'rcs': {
                'type': 'rcs',
                'name': 'RCS',
                'generator': RcsGenerator(),
                'template': None,
                'use_class': True
            },
            'other': {
                'type': 'other',
                'name': 'OTHER',
                'generator': OtherGenerator(),
                'template': None,
                'use_class': True
            },
            'tr': {
                'type': 'tr',
                'name': 'TR',
                'generator': TrGenerator(),
                'template': None,
                'use_class': True
            },
            'tm': {
                'type': 'tm',
                'name': 'TM',
                'generator': TmGenerator(),
                'template': None,
                'use_class': True
            },
            'pm': {
                'type': 'pm',
                'name': 'PM',
                'generator': PmGenerator(),
                'template': None,
                'use_class': True
            }
        }
    
    def get_all_document_types(self):
        """获取所有文档类型配置"""
        return list(self.generators.values())
    
    def get_generator(self, doc_type):
        """获取指定类型的生成器配置"""
        return self.generators.get(doc_type)
    
    def _handle_if_document(self, generator, generation_data, docx_path, template_name, output_format):
        """处理IF文档的特殊逻辑"""
        try:
            # 调用IF生成器函数
            result = generator(generation_data, docx_path, template_name)
            
            # IF生成器返回字典，检查success字段
            if isinstance(result, dict):
                if result.get('success', False):
                    if output_format == 'pdf':
                        # 转换为PDF
                        pdf_filename = os.path.basename(docx_path).replace('.docx', '.pdf')
                        pdf_path = docx_path.replace('.docx', '.pdf')
                        
                        pdf_success = generate_if_pdf_from_docx(docx_path, pdf_path)
                        
                        if pdf_success:
                            return {
                                "success": True,
                                "filename": pdf_filename,
                                "file_path": pdf_path,
                                "download_url": f"/api/mvp/download/{pdf_filename}"
                            }
                        else:
                            return {"success": False, "error": "PDF转换失败"}
                    else:
                        return {
                            "success": True,
                            "filename": os.path.basename(docx_path),
                            "file_path": docx_path,
                            "download_url": f"/api/mvp/download/{os.path.basename(docx_path)}"
                        }
                else:
                    error_msg = result.get('message', result.get('error', 'Word文档生成失败'))
                    return {"success": False, "error": error_msg}
            else:
                return {"success": False, "error": f"IF生成器返回了无效的结果类型: {type(result)}"}
                
        except Exception as e:
            print(f"IF文档处理异常: {str(e)}")
            return {"success": False, "error": f"IF文档处理异常: {str(e)}"}

def _prepare_generation_data(form_data):
    """准备文档生成所需的数据"""
    return {
        # 基本信息字段
        "approval_no": form_data.approval_no,
        "information_folder_no": form_data.information_folder_no,
        "safety_class": form_data.safety_class,
        "pane_desc": form_data.pane_desc,
        "glass_layers": form_data.glass_layers,
        "interlayer_layers": form_data.interlayer_layers,
        "windscreen_thick": form_data.windscreen_thick,
        "interlayer_thick": form_data.interlayer_thick,
        "glass_treatment": form_data.glass_treatment,
        "interlayer_type": form_data.interlayer_type,
        "coating_type": form_data.coating_type,
        "coating_thick": form_data.coating_thick,
        "material_nature": form_data.material_nature,
        "coating_color": form_data.coating_color,
        # 新增字段 - 玻璃颜色和夹层相关
        "glass_color_choice": form_data.glass_color_choice,
        "interlayer_total": form_data.interlayer_total,
        "interlayer_partial": form_data.interlayer_partial,
        "interlayer_colourless": form_data.interlayer_colourless,
        # 新增字段 - 导体和不透明相关
        "conductors_choice": form_data.conductors_choice,
        "opaque_obscure_choice": form_data.opaque_obscure_choice,
        "remarks": form_data.remarks,
        # 报告号
        "report_no": form_data.report_no,
        # 新增日期字段
        "approval_date": form_data.approval_date,
        "test_date": form_data.test_date,
        "report_date": form_data.report_date,
        # 公司信息（现在完全来自formData，不再查询company表）
        "company_id": form_data.company_id,
        "company_name": form_data.company_name,
        "company_address": form_data.company_address or '',
        "trade_names": form_data.trade_names or '',
        "trade_marks": form_data.trade_marks or [],
        "vehicles": form_data.vehicles or []
    }

def _generate_single_document(doc_info, generation_data, output_dir, safe_approval_no, output_format):
    """生成单个文档"""
    doc_type = doc_info.get('type', 'unknown')
    doc_name = doc_info['name']
    generator = doc_info['generator']
    template_name = doc_info['template']
    use_class = doc_info['use_class']
    special_handler = doc_info.get('special_handler')
    
    try:
        if special_handler:
            # 使用特殊处理器（如IF文档）
            docx_filename = f"{doc_name}-{safe_approval_no}.docx"
            docx_path = os.path.join(output_dir, docx_filename)
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            result = special_handler(generator, generation_data, docx_path, template_name, output_format)
            return result
        
        else:
            # 其他文档类型
            # 根据输出格式确定文件名和路径
            if output_format == 'pdf':
                filename = f"{doc_name}-{safe_approval_no}.pdf"
                file_path = os.path.join(output_dir, filename)
            else:
                filename = f"{doc_name}-{safe_approval_no}.docx"
                file_path = os.path.join(output_dir, filename)
            
            if use_class:
                # 使用生成器类
                result = generator.generate_document(generation_data, file_path, output_format)
                
                if result.get('success'):
                    return {
                        "success": True,
                        "filename": filename,
                        "file_path": file_path,
                        "download_url": f"/api/mvp/download/{filename}"
                    }
                else:
                    return result
            else:
                # 使用生成器函数
                result = generator(generation_data, file_path, output_format)
                
                if result.get('success'):
                    return {
                        "success": True,
                        "filename": filename,
                        "file_path": file_path,
                        "download_url": f"/api/mvp/download/{filename}"
                    }
                else:
                    return result
            
            # 处理生成器返回的结果已经在上面处理了，这里不需要额外处理
                
    except Exception as e:
        print(f"生成异常: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return {"success": False, "error": f"生成失败: {str(e)}"}



@mvp_bp.route('/save-form-data', methods=['POST'])
def save_form_data():
    """保存表单数据"""
    try:

        data = request.get_json()
        session_id = data.get('session_id')
        form_data = data.get('form_data', {})
        
        # 如果session_id为空，自动生成一个正式的session_id
        if not session_id:
            import uuid
            import time
            # 生成格式：session_时间戳_随机UUID
            timestamp = int(time.time())
            random_uuid = uuid.uuid4().hex[:8]
            session_id = f"session_{timestamp}_{random_uuid}"
            print(f"🆔 自动生成session_id: {session_id}")
        
        # 使用FormData.query查询
        existing_form = FormData.query.filter_by(session_id=session_id).first()
        
        if existing_form:
            # 更新现有记录
            print("📝 更新现有记录")
            for key, value in form_data.items():
                if hasattr(existing_form, key):
                    # 特殊处理日期字段
                    if key in ['approval_date', 'test_date', 'report_date']:
                        if isinstance(value, str) and value:
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                continue  # 跳过无效日期
                        elif not value:
                            continue  # 跳过空值，保持原有值
                    setattr(existing_form, key, value)
            existing_form.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            print("📝 创建新记录")
            # 处理日期字段
            approval_date = form_data.get('approval_date')
            test_date = form_data.get('test_date')
            report_date = form_data.get('report_date')
            
            # 如果前端传递的是字符串，转换为date对象
            if isinstance(approval_date, str) and approval_date:
                try:
                    approval_date = datetime.strptime(approval_date, '%Y-%m-%d').date()
                except ValueError:
                    approval_date = None
            else:
                approval_date = None
                
            if isinstance(test_date, str) and test_date:
                try:
                    test_date = datetime.strptime(test_date, '%Y-%m-%d').date()
                except ValueError:
                    test_date = None
            else:
                test_date = None
                
            if isinstance(report_date, str) and report_date:
                try:
                    report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
                except ValueError:
                    report_date = None
            else:
                report_date = None
            
            new_form = FormData(
                session_id=session_id,
                title=form_data.get('title', ''),
                # IF_Template.docx 相关字段
                approval_no=form_data.get('approval_no', ''),
                information_folder_no=form_data.get('information_folder_no', ''),
                safety_class=form_data.get('safety_class', ''),
                pane_desc=form_data.get('pane_desc', ''),
                glass_layers=form_data.get('glass_layers', ''),
                interlayer_layers=form_data.get('interlayer_layers', ''),
                windscreen_thick=form_data.get('windscreen_thick', ''),
                interlayer_thick=form_data.get('interlayer_thick', ''),
                glass_treatment=form_data.get('glass_treatment', ''),
                interlayer_type=form_data.get('interlayer_type', ''),
                coating_type=form_data.get('coating_type', ''),
                coating_thick=form_data.get('coating_thick', ''),
                material_nature=form_data.get('material_nature', ''),
                coating_color=form_data.get('coating_color', ''),
                # 新增字段 - 玻璃颜色和夹层相关
                glass_color_choice=form_data.get('glass_color_choice', 'tinted_struck'),
                interlayer_total=form_data.get('interlayer_total', False),
                interlayer_partial=form_data.get('interlayer_partial', False),
                interlayer_colourless=form_data.get('interlayer_colourless', False),
                # 新增字段 - 导体和不透明相关
                conductors_choice=form_data.get('conductors_choice', 'yes_struck'),
                opaque_obscure_choice=form_data.get('opaque_obscure_choice', 'yes_struck'),
                remarks=form_data.get('remarks', ''),
                report_no=form_data.get('report_no', ''),
                company_id=form_data.get('company_id'),
                company_name=form_data.get('company_name', ''),
                company_address=form_data.get('company_address', ''),
                trade_names=form_data.get('trade_names', ''),
                trade_marks=form_data.get('trade_marks', []),
                vehicles=form_data.get('vehicles', []),
                # 新增日期字段
                approval_date=approval_date,
                test_date=test_date,
                report_date=report_date,
                status=form_data.get('status', 'draft')
            )
            db.session.add(new_form)
        
        db.session.commit()
        print("✅ 数据保存成功")
        
        return jsonify({
            "success": True,
            "message": "表单数据保存成功",
            "data": {
                "saved_at": datetime.utcnow().isoformat(),
                "version": "1.0",
                "session_id": session_id,  # 返回session_id，包括新生成的正式ID
            }
        })
        
    except Exception as e:
        print(f"❌ 保存表单数据失败: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"error": f"保存表单数据失败: {str(e)}"}), 500

@mvp_bp.route('/get-form-data/<session_id>', methods=['GET'])
def get_form_data(session_id):
    """获取表单数据"""
    try:
        form_data = FormData.query.filter_by(session_id=session_id).first()
        
        if not form_data:
            return jsonify({"error": "未找到表单数据"}), 404
        
        return jsonify({
            "success": True,
            "data": {
                "session_id": form_data.session_id,
                "title": form_data.title,
                # IF_Template.docx 相关字段
                "approval_no": form_data.approval_no,
                "information_folder_no": form_data.information_folder_no,
                "safety_class": form_data.safety_class,
                "pane_desc": form_data.pane_desc,
                "glass_layers": form_data.glass_layers,
                "interlayer_layers": form_data.interlayer_layers,
                "windscreen_thick": form_data.windscreen_thick,
                "interlayer_thick": form_data.interlayer_thick,
                "glass_treatment": form_data.glass_treatment,
                "interlayer_type": form_data.interlayer_type,
                "coating_type": form_data.coating_type,
                "coating_thick": form_data.coating_thick,
                "material_nature": form_data.material_nature,
                "coating_color": form_data.coating_color,
                "remarks": form_data.remarks,
                "report_no": form_data.report_no,
                "company_id": form_data.company_id,
                "company_name": form_data.company_name,
                "company_address": form_data.company_address,
                "trade_names": form_data.trade_names,
                "trade_marks": form_data.trade_marks or [],
                "vehicles": form_data.vehicles or [],
                # 新增日期字段
                "approval_date": form_data.approval_date.isoformat() if form_data.approval_date else None,
                "test_date": form_data.test_date.isoformat() if form_data.test_date else None,
                "report_date": form_data.report_date.isoformat() if form_data.report_date else None,
                "status": form_data.status,
                "created_at": form_data.created_at.isoformat(),
                "updated_at": form_data.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"❌ 获取表单数据失败: {str(e)}")
        return jsonify({"error": f"获取表单数据失败: {str(e)}"}), 500




@mvp_bp.route('/generate-documents', methods=['POST'])
def generate_all_documents():
    """生成所有类型的文档"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        output_format = data.get('output_format', 'docx')  # docx 或 pdf
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        # 获取表单数据
        form_data = FormData.query.filter_by(session_id=session_id).first()
        if not form_data:
            return jsonify({"error": "未找到表单数据"}), 404
        
        # 准备生成数据
        generation_data = _prepare_generation_data(form_data)
        
        # 处理Approval_No生成文件名
        safe_approval_no = _make_safe_approval_no(form_data)
        
        # 确保输出目录存在
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用工厂类获取所有文档类型配置
        factory = DocumentGeneratorFactory()
        all_document_types = factory.get_all_document_types()
        
        # 生成所有类型的文档
        generated_files = []
        failed_documents = []
        
        for doc_info in all_document_types:
            result = _generate_single_document(
                doc_info, generation_data, output_dir, safe_approval_no, output_format
            )
            
            if result['success']:
                generated_files.append({
                    "type": doc_info['name'],
                    "filename": result['filename'],
                    "file_path": result['file_path'],
                    "download_url": result['download_url']
                })
            else:
                failed_documents.append({"type": doc_info['name'], "error": result['error']})
        
        # 返回生成结果
        if generated_files:
            return jsonify({
                "success": True,
                "message": f"成功生成 {len(generated_files)} 个文档",
                "data": {
                    "generated_files": generated_files,
                    "failed_documents": failed_documents,
                    "total_requested": len(all_document_types),
                    "total_success": len(generated_files),
                    "total_failed": len(failed_documents)
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "所有文档生成失败",
                "data": {
                    "failed_documents": failed_documents,
                    "total_requested": len(all_document_types),
                    "total_failed": len(failed_documents)
                }
            }), 500
        
    except Exception as e:
        print(f"❌ 生成所有文档失败: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"生成所有文档失败: {str(e)}"}), 500

@mvp_bp.route('/generate-if', methods=['POST'])
def generate_if():
    """生成IF文档"""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        output_format = data.get('output_format') or data.get('format', 'docx')
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        return _generate_single_document_by_type('if', session_id, output_format)
        
    except Exception as e:
        print(f"🔥 IF文档生成接口异常: {str(e)}")
        import traceback
        print(f"🔍 错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"IF文档生成接口异常: {str(e)}"}), 500
# ========== 新增：多类型测试文档生成接口 ==========

@mvp_bp.route('/generate-cert', methods=['POST'])
def generate_cert():
    """生成CERT文档"""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        return _generate_single_document_by_type('cert', session_id, format_type)
        
    except Exception as e:
        print(f"🔥 CERT文档生成接口异常: {str(e)}")
        import traceback
        print(f"🔍 错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"CERT文档生成接口异常: {str(e)}"}), 500


@mvp_bp.route('/generate-other', methods=['POST'])
def generate_other():
    """生成OTHER文档"""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        return _generate_single_document_by_type('other', session_id, format_type)
        
    except Exception as e:
        print(f"🔥 OTHER文档生成接口异常: {str(e)}")
        import traceback
        print(f"🔍 错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"OTHER文档生成接口异常: {str(e)}"}), 500


@mvp_bp.route('/generate-tr', methods=['POST'])
def generate_tr():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')  # 支持docx和pdf格式
        form_data = FormData.query.filter_by(session_id=session_id).first() if session_id else None
        
        # 准备TR测试报告数据
        tr_data = {}
        if form_data:
            # 只保留模板中实际存在的变量
            tr_data = {
                'report_no': form_data.report_no,
                'company_name': form_data.company_name,
                'approval_no': form_data.approval_no,
                'trade_names': form_data.trade_names,
                'trade_marks': form_data.trade_marks,
                'company_address': form_data.company_address,
                'information_folder_no': form_data.information_folder_no,
                'approval_date': form_data.approval_date,
                'report_date': form_data.report_date,
                'safety_class': form_data.safety_class,
                'windscreen_thick': form_data.windscreen_thick,
                'glass_layers': form_data.glass_layers,
                'interlayer_layers': form_data.interlayer_layers,
                'interlayer_thick': form_data.interlayer_thick,
                'glass_treatment': form_data.glass_treatment,
                'interlayer_type': form_data.interlayer_type,
                'coating_type': form_data.coating_type,
                'coating_thick': form_data.coating_thick,
                'test_date': form_data.test_date,
                'vehicles': form_data.vehicles or []
            }
        else:
            # 使用示例数据
            tr_data = create_tr_sample_data()
        
        # 生成输出路径
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        file_ext = '.pdf' if format_type == 'pdf' else '.docx'
        
        # 使用安全的approval_no生成文件名
        if form_data:
            safe_approval_no = _make_safe_approval_no(form_data, 'TR-2024-001')
        else:
            safe_approval_no = 'TR-2024-001'
            
        filename = f"TR-{safe_approval_no}{file_ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 生成TR测试报告
        result = generate_tr_document(tr_data, output_path, format_type)
        
        if result["success"]:
            payload = {
                "filename": filename,
                "file_path": output_path,
                "download_url": f"/api/mvp/download/{filename}"
            }
            return jsonify({"success": True, "message": "TR测试报告生成成功", "data": payload})
        else:
            return jsonify({"error": result["message"]}), 500
            
    except Exception as e:
        return jsonify({"error": f"TR测试报告生成失败: {str(e)}"}), 500


@mvp_bp.route('/generate-review-control-sheet', methods=['POST'])
def generate_review_control_sheet():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')  # 支持docx和pdf格式
        form_data = FormData.query.filter_by(session_id=session_id).first() if session_id else None
        
        # 准备RCS审查控制表数据
        rcs_data = {}
        if form_data:
            rcs_data = {
                # 必需的变量
                'report_no': form_data.report_no or 'RCS-REPORT-2024-001',
                'approval_no': form_data.approval_no or 'RCS-APPROVAL-2024-001',
                'company_name': form_data.company_name or '示例企业名称',
                'windscreen_thick': form_data.windscreen_thick or '5.0mm',
            }
        else:
            # 使用示例数据
            rcs_data = create_rcs_sample_data()
        
        # 生成输出路径
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = '.pdf' if format_type == 'pdf' else '.docx'
        approval_no = form_data.approval_no if form_data else 'RCS-2024-001'
        # 使用安全文件名，避免特殊字符导致的文件系统错误
        safe_approval_no = _make_safe_approval_no(form_data, 'RCS-2024-001')
        filename = f"Review Control Sheet V7 {safe_approval_no}{file_ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 生成RCS审查控制表
        result = generate_rcs_document(rcs_data, output_path, format_type)
        
        if result["success"]:
            payload = {
                "filename": filename,
                "file_path": output_path,
                "download_url": f"/api/mvp/download/{filename}"
            }
            return jsonify({"success": True, "message": "RCS审查控制表生成成功", "data": payload})
        else:
            return jsonify({"error": result["message"]}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"RCS审查控制表生成失败: {str(e)}"}), 500


@mvp_bp.route('/generate-tm', methods=['POST'])
def generate_tm():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')  # 支持docx和pdf格式
        form_data = FormData.query.filter_by(session_id=session_id).first() if session_id else None
        
        # 准备TM测试记录数据
        tm_data = {}
        if form_data:
            # 只保留模板中实际存在的变量
            tm_data = {
                'test_date': form_data.test_date,
                'windscreen_thick': form_data.windscreen_thick,
                'glass_layers': form_data.glass_layers,
                'interlayer_layers': form_data.interlayer_layers,
                'interlayer_thick': form_data.interlayer_thick,
                'glass_treatment': form_data.glass_treatment,
                'interlayer_type': form_data.interlayer_type,
                'coating_type': form_data.coating_type,
                'coating_thick': form_data.coating_thick,
                'material_nature': form_data.material_nature,
                'coating_color': form_data.coating_color,
                'interlayer_total': form_data.interlayer_total,
                'conductors_choice': form_data.conductors_choice,
                'opaque_obscure_choice': form_data.opaque_obscure_choice,
                'glass_color_choice': form_data.glass_color_choice
            }
        else:
            # 使用示例数据
            tm_data = create_tm_sample_data()
        
        # 生成输出路径
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        file_ext = '.pdf' if format_type == 'pdf' else '.docx'
        
        # 使用安全的approval_no生成文件名
        if form_data:
            safe_approval_no = _make_safe_approval_no(form_data, 'TM-2024-001')
        else:
            safe_approval_no = 'TM-2024-001'
            
        filename = f"TM-{safe_approval_no}{file_ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 生成TM测试记录
        result = generate_tm_document(tm_data, output_path, format_type)
        
        if result["success"]:
            payload = {
                "filename": filename,
                "file_path": output_path,
                "download_url": f"/api/mvp/download/{filename}"
            }
            return jsonify({"success": True, "message": "TM测试记录生成成功", "data": payload})
        else:
            return jsonify({"error": result["message"]}), 500
            
    except Exception as e:
        return jsonify({"error": f"TM测试记录生成失败: {str(e)}"}), 500


@mvp_bp.route('/generate-project-sheet', methods=['POST'])
def generate_project_sheet():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')  # 支持docx和pdf格式
        form_data = FormData.query.filter_by(session_id=session_id).first() if session_id else None
        
        # 准备PM项目管理表数据
        pm_data = {}
        if form_data:
            pm_data = {
                'project_name': '汽车安全玻璃认证项目',
                'project_number': form_data.approval_no or 'PM-2024-001',
                'project_manager': '王五',
                'project_manager_phone': '010-12345678',
                'project_manager_email': 'pm@example.com',
                'company_name': form_data.company_name or '示例企业名称',
                'approval_date': form_data.approval_date,
                'test_date': form_data.test_date,
                'report_date': form_data.report_date,
                'actual_end_date': '2024-06-15',
                'project_status': '进行中',
                'project_phase': '技术评审阶段',
                'project_scope': '汽车安全玻璃质量管理体系认证',
                'project_objectives': [
                    '建立完善的质量管理体系',
                    '通过TÜV NORD认证审核',
                    '获得相关产品认证证书'
                ],
                'key_milestones': [
                    {'name': '项目启动', 'date': '2024-01-01', 'status': '已完成'},
                    {'name': '体系建立', 'date': '2024-03-15', 'status': '已完成'},
                    {'name': '内部审核', 'date': '2024-04-30', 'status': '已完成'},
                    {'name': '外部审核', 'date': '2024-06-15', 'status': '进行中'},
                    {'name': '项目完成', 'date': '2024-06-30', 'status': '计划中'}
                ],
                'team_members': [
                    {'name': '王五', 'role': '项目经理', 'phone': '010-12345678'},
                    {'name': '李四', 'role': '技术负责人', 'phone': '010-12345679'},
                    {'name': '张三', 'role': '质量负责人', 'phone': '010-12345680'}
                ],
                'budget': {
                    'total_budget': 500000,
                    'used_budget': 350000,
                    'remaining_budget': 150000,
                    'currency': 'CNY'
                },
                'risks': [
                    {'risk': '技术标准变更', 'impact': '高', 'mitigation': '密切关注标准更新'},
                    {'risk': '审核延期', 'impact': '中', 'mitigation': '提前准备审核材料'},
                    {'risk': '人员变动', 'impact': '低', 'mitigation': '建立知识传承机制'}
                ],
                'next_actions': [
                    '完成外部审核准备',
                    '整理认证申请材料',
                    '安排最终技术评审'
                ],
                'approval_status': '已批准',
                'approver_name': '赵六',
                'approver_title': '技术总监'
            }
        else:
            # 使用示例数据
            pm_data = create_pm_sample_data()
        
        # 生成输出路径
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        file_ext = '.pdf' if format_type == 'pdf' else '.docx'
        approval_no = form_data.approval_no if form_data else 'PM-2024-001'
        filename = f"PM-{approval_no}{file_ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 生成PM项目管理表
        result = generate_pm_document(pm_data, output_path, format_type)
        
        if result["success"]:
            payload = {
                "filename": filename,
                "file_path": output_path,
                "download_url": f"/api/mvp/download/{filename}"
            }
            return jsonify({"success": True, "message": "PM项目管理表生成成功", "data": payload})
        else:
            return jsonify({"error": result["message"]}), 500
            
    except Exception as e:
        return jsonify({"error": f"PM项目管理表生成失败: {str(e)}"}), 500

def _generate_single_document_by_type(doc_type, session_id, output_format='docx'):
    """通用的单文档生成函数"""
    try:
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        # 获取表单数据
        form_data = FormData.query.filter_by(session_id=session_id).first()
        if not form_data:
            return jsonify({"error": "未找到表单数据"}), 404
        
        # 准备生成数据
        generation_data = _prepare_generation_data(form_data)
        
        # 处理Approval_No生成文件名
        safe_approval_no = _make_safe_approval_no(form_data)
        
        # 确保输出目录存在
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用工厂类获取文档配置
        factory = DocumentGeneratorFactory()
        doc_config = factory.get_generator(doc_type)
        
        if not doc_config:
            return jsonify({"error": f"{doc_type.upper()}文档生成器配置不存在"}), 500
        
        # 生成文档
        result = _generate_single_document(
            doc_config, generation_data, output_dir, safe_approval_no, output_format
        )
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": f"{doc_config['name']} {output_format.upper()}文档生成成功",
                "data": {
                    "filename": result['filename'],
                    "file_path": result['file_path'],
                    "download_url": result['download_url']
                }
            })
        else:
            return jsonify({"error": result['error']}), 500
        
    except Exception as e:
        print(f"❌ 生成{doc_type.upper()}文档失败: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"生成{doc_type.upper()}文档失败: {str(e)}"}), 500

@mvp_bp.route('/download/<filename>', methods=['GET'])
def download_generated_document(filename):
    """下载生成的文档"""
    try:
        # 安全检查：防止路径遍历攻击
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({"error": "无效的文件名"}), 400
        
        # 构建文件路径
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files', filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({"error": "文件不存在"}), 404
        
        # 检查文件是否为普通文件
        if not os.path.isfile(file_path):
            return jsonify({"error": "无效的文件"}), 400
        
        # 使用 send_file 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        print(f"❌ 下载文件失败: {str(e)}")
        return jsonify({"error": f"下载失败: {str(e)}"}), 500
        
@mvp_bp.route('/ai-extract', methods=['POST'])
def ai_extract_document():
    """AI文档信息提取"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "未找到上传的文件"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "未选择文件"
            }), 400
        
        # 检查文件类型
        allowed_extensions = {'.doc', '.docx', '.pdf'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                "success": False,
                "error": f"不支持的文件类型: {file_ext}，仅支持: {', '.join(allowed_extensions)}"
            }), 400
        
        # 保存上传的文件到临时目录
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'temp')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        temp_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_file_path = os.path.join(upload_dir, temp_filename)
        
        try:
            file.save(temp_file_path)
            
            # 调用AI提取服务
            extraction_result = ai_extraction_service.extract_from_document(temp_file_path)
            
            if extraction_result["success"]:
                return jsonify({
                    "success": True,
                    "message": "AI提取成功",
                    "data": extraction_result["data"]
                })
            else:
                return jsonify({
                    "success": False,
                    "error": extraction_result.get("error", "AI提取失败")
                }), 500
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        current_app.logger.error(f"AI提取失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"AI提取失败: {str(e)}"
        }), 500 